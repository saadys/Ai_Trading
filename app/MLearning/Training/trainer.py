import sys
import os
import logging
# Fix OpenMP runtime error: initializing libiomp5md.dll, but found libiomp5md.dll already initialized
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

import numpy as np
import pandas as pd


from app.MLearning.LSTM_Model.model import LSTM_Production_Model
from app.MLearning.LSTM_Model.Config import Config
from app.MLearning.preprocessing.CryptoDataProcessor import CryptoDataProcessor 

import copy
from typing import Tuple, List, Optional
from sklearn.preprocessing import RobustScaler
import joblib


import mlflow

mlflow.set_tracking_uri("postgresql://postgres:saadys@localhost:5432/mlflow_db")
mlflow.set_experiment("Cène (dernier repas)")



class EarlyStopping:
    def __init__(self, patience=10, verbose=False, delta=0, path='checkpoint.pt'):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = float('inf')
        self.delta = delta
        self.path = path
        self.best_model_state = None

    def __call__(self, val_loss, model):
        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.verbose:
                logger.info(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            logger.info(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        self.best_model_state = copy.deepcopy(model.state_dict())
        self.val_loss_min = val_loss

class Trainer:
    def __init__(self, 
                 model: nn.Module, 
                 device: torch.device = None,
                 learning_rate: float = 0.001,
                 patience: int = 10,
                 accumulation_steps: int = 4,
                 model_info: dict = None):
        
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = model.to(self.device)
        
        # Use BCE Loss since Q-Labels represent values in [0, 1] essentially framing it as probability
        self.criterion = nn.BCELoss()
        
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=1e-5  
        )
        
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
        
        self.max_grad_norm = 1.0
        
        self.learning_rate = learning_rate
        self.patience = patience
        self.early_stopping = EarlyStopping(patience=patience, verbose=True)
        self.accumulation_steps = accumulation_steps
        self.model_info = model_info

    def fit(self, 
            train_loader: DataLoader, 
            val_loader: DataLoader, 
            epochs: int = 100) -> nn.Module:
        
        logger.info(f"Starting training on {self.device} for {epochs} epochs...")
        
        train_losses = []
        val_losses = []
        with mlflow.start_run() as run:
            mlflow.log_params({
                "learning_rate": self.learning_rate,
                "patience": self.patience,
                "accumulation_steps": self.accumulation_steps
            })
            for epoch in range(epochs):
                self.model.train()
                running_loss = 0.0
                self.optimizer.zero_grad()
                
                for i, (X_batch, y_batch) in enumerate(train_loader):
                    X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                    
                    outputs = self.model(X_batch)
                    if outputs.shape != y_batch.shape:
                        outputs = outputs.view_as(y_batch)

                    loss = self.criterion(outputs, y_batch)
                    
                    loss = loss / self.accumulation_steps
                    loss.backward()
                    
                    if (i + 1) % self.accumulation_steps == 0:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            max_norm=self.max_grad_norm
                        )
                        self.optimizer.step()
                        self.optimizer.zero_grad()
                    
                    running_loss += loss.item() * X_batch.size(0) * self.accumulation_steps
                
                if (i + 1) % self.accumulation_steps != 0:
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        max_norm=self.max_grad_norm
                    )
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                
                epoch_train_loss = running_loss / len(train_loader.dataset)
                train_losses.append(epoch_train_loss)
                
                self.model.eval()
                val_running_loss = 0.0
                
                all_preds = []
                all_targets = []

                with torch.no_grad():
                    for X_val, y_val in val_loader:
                        X_val, y_val = X_val.to(self.device), y_val.to(self.device)
                        outputs = self.model(X_val)
                        if outputs.shape != y_val.shape:
                            outputs = outputs.view_as(y_val)
                        loss = self.criterion(outputs, y_val)
                        val_running_loss += loss.item() * X_val.size(0)
                        
                        all_preds.append(outputs.cpu().numpy())
                        all_targets.append(y_val.cpu().numpy())
                
                all_preds = np.concatenate(all_preds).flatten()
                all_targets = np.concatenate(all_targets).flatten()
                
                epoch_val_loss = val_running_loss / len(val_loader.dataset)
                val_losses.append(epoch_val_loss)

                mae = np.mean(np.abs(all_preds - all_targets))
                rmse = np.sqrt(np.mean((all_preds - all_targets)**2))
                epsilon = 1e-8
                mape = np.mean(np.abs((all_targets - all_preds) / (all_targets + epsilon))) * 100
                
                # R2 Score
                ss_res = np.sum((all_targets - all_preds)**2)
                ss_tot = np.sum((all_targets - np.mean(all_targets))**2)
                r2_score = 1 - (ss_res / (ss_tot + epsilon))
                
                if epoch == 0:
                    logger.info("DIAGNOSTIC (Epoch 1):")
                    logger.info(f"Predictions: min={all_preds.min():.4f}, max={all_preds.max():.4f}, mean={all_preds.mean():.4f}, std={all_preds.std():.4f}")
                    logger.info(f"Targets: min={all_targets.min():.4f}, max={all_targets.max():.4f}, mean={all_targets.mean():.4f}, std={all_targets.std():.4f}")
                    logger.info(f"Pred variance: {all_preds.std():.6f} (should be > 0.01)")
                    if all_preds.std() < 0.01:
                        logger.warning("Model is predicting almost constant values!")

                logger.info(f'Epoch {epoch+1}/{epochs} | Train Loss: {epoch_train_loss:.6f} | Val Loss: {epoch_val_loss:.6f} | R2: {r2_score:.4f}')
                
                self.early_stopping(epoch_val_loss, self.model)

                self.scheduler.step(epoch_val_loss)

                current_lr = self.optimizer.param_groups[0]['lr']

                mlflow.log_metrics(
                    {
                        "train_loss": epoch_train_loss,
                        "val_loss": epoch_val_loss,
                        "MAE": mae,
                        "RMSE": rmse,
                        "MAPE": mape,
                        "R2_Score": r2_score,
                        "learning_rate": current_lr
                    },
                    step=epoch
                )

                if self.early_stopping.early_stop:
                    logger.info("Early stopping triggered.")
                    break

            # Restore best model AFTER the loop
            if self.early_stopping.best_model_state:
                self.model.load_state_dict(self.early_stopping.best_model_state)
                logger.info("Loaded best model state from early stopping checkpoint.")

            self.model_info = mlflow.pytorch.log_model(self.model, name="final_model")

                

        return self.model

    def quantize_model(self, save_path: str = "models/lstm_model_quantized.pth"):
        logger.info("Applying Dynamic Quantization...")
        self.model.to('cpu')
        self.model.eval()
        
        quantized_model = torch.quantization.quantize_dynamic(
            self.model, {nn.LSTM, nn.Linear}, dtype=torch.qint8
        )
        
        logger.info(f"Quantization complete. Saving to {save_path}...")
        torch.save(quantized_model.state_dict(), save_path)
        return quantized_model

class AdvancedDataPipeline:
    def __init__(self, csv_path: str, lookback: int = 192, batch_size: int = 128):
        self.csv_path = csv_path
        self.lookback = lookback
        self.batch_size = batch_size
        self.scaler = RobustScaler()
        
        self.feature_cols = [
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
            'dist_ema_50', 'dist_ema_200', 
            'rsi_norm', 'atr_ratio', 
            'macd_norm', 'macd_sig_norm', 'macd_hist_norm', 
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos', 
            'Volume_log', 
            'VMD_Mode1_diff', 'VMD_Mode2', 'VMD_Mode3'  
        ]
        self.target_col = 'Target'

    def load_and_prep(self) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
        logger.info(f"Loading CSV from {self.csv_path}...")
        try:
            df = pd.read_csv(self.csv_path)
            if 'Open time' in df.columns:
                df['Open time'] = pd.to_datetime(df['Open time'])
                df = df.sort_values('Open time').reset_index(drop=True)
        except Exception as e:
            logger.exception(f"Error reading CSV file: {e}")
            raise
 
        initial_len = len(df)
        df = df.dropna()
        dropped_len = len(df)
        logger.info(f"Dropped {initial_len - dropped_len} row(s) containing NaNs.")
        
        if dropped_len == 0:
            raise ValueError("All data dropped! Check your data source.")

        missing_cols = [c for c in self.feature_cols if c not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns {missing_cols}. Ignoring them.")
            self.feature_cols = [c for c in self.feature_cols if c in df.columns]

        n = len(df)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)
        scale_cols = [
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
            'dist_ema_50', 'dist_ema_200',
            'atr_ratio',
            'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
            'Volume_log',
            'VMD_Mode1_diff', 'VMD_Mode2', 'VMD_Mode3' 
        ]
        
        passthrough_cols = [
            'hour_sin', 'hour_cos',
            'day_of_week_sin', 'day_of_week_cos',
            'month_sin', 'month_cos',
            'rsi_norm' 
        ]
        
        logger.info(f"Features to scale: {len(scale_cols)}")
        logger.info(f"Features passthrough (pre-normalized): {len(passthrough_cols)}")
        
        # Ensure all columns are present
        scale_cols = [c for c in scale_cols if c in self.feature_cols]
        passthrough_cols = [c for c in passthrough_cols if c in self.feature_cols]

        # Prepare Raw splits
        X_train_raw = df.iloc[:train_idx]
        X_val_raw = df.iloc[train_idx:val_idx]
        X_test_raw = df.iloc[val_idx:]

        y_train_raw = df[self.target_col].iloc[:train_idx].values.reshape(-1, 1)
        y_val_raw = df[self.target_col].iloc[train_idx:val_idx].values.reshape(-1, 1)
        y_test_raw = df[self.target_col].iloc[val_idx:].values.reshape(-1, 1)

        logger.info("Fitting scalers on training data...")
        
        # Fit scaler on scale_cols
        if scale_cols:
            X_train_scale_part = self.scaler.fit_transform(X_train_raw[scale_cols].values)
            X_val_scale_part = self.scaler.transform(X_val_raw[scale_cols].values)
            X_test_scale_part = self.scaler.transform(X_test_raw[scale_cols].values)
        else:
            X_train_scale_part = np.empty((len(X_train_raw), 0))
            X_val_scale_part = np.empty((len(X_val_raw), 0))
            X_test_scale_part = np.empty((len(X_test_raw), 0))
        
        # Get passthrough parts
        X_train_pass = X_train_raw[passthrough_cols].values
        X_val_pass = X_val_raw[passthrough_cols].values
        X_test_pass = X_test_raw[passthrough_cols].values
        
        # Concatenate back: Scaled + Passthrough
        X_train_final = np.hstack([X_train_scale_part, X_train_pass])
        X_val_final = np.hstack([X_val_scale_part, X_val_pass])
        X_test_final = np.hstack([X_test_scale_part, X_test_pass])
        
        # Target is Q-Label [0,1], no scaling needed
        logger.info("Target is Q-Labels [0,1]. No target scaling applied.")
        y_train_scaled = y_train_raw.flatten()
        y_val_scaled = y_val_raw.flatten()
        y_test_scaled = y_test_raw.flatten()
        
        logger.info(f"Target distribution: mean={y_train_scaled.mean():.4f}, std={y_train_scaled.std():.4f}")

        X_train_seq, y_train_seq = self._create_sequences(X_train_final, y_train_scaled)
        X_val_seq, y_val_seq = self._create_sequences(X_val_final, y_val_scaled)
        X_test_seq, y_test_seq = self._create_sequences(X_test_final, y_test_scaled)

        logger.info(f"Train seq: {X_train_seq.shape}, Val seq: {X_val_seq.shape}, Test seq: {X_test_seq.shape}")

        # 6. Create DataLoaders
        train_loader = DataLoader(TensorDataset(torch.FloatTensor(X_train_seq), torch.FloatTensor(y_train_seq)), 
                                  batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(TensorDataset(torch.FloatTensor(X_val_seq), torch.FloatTensor(y_val_seq)), 
                                batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(TensorDataset(torch.FloatTensor(X_test_seq), torch.FloatTensor(y_test_seq)), 
                                 batch_size=self.batch_size, shuffle=False)
        
        input_size = X_train_seq.shape[2]
        return train_loader, val_loader, test_loader, input_size

    def _create_sequences(self, X, y):

        Xs, ys = [], []
        for i in range(self.lookback - 1, len(X)):

            Xs.append(X[i - self.lookback + 1 : i + 1])
            ys.append(y[i])
        return np.array(Xs), np.array(ys)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # trainer.py est à Ai_Trading/app/MLearning/Training/
    # enriched_data.csv est produit par CryptoDataProcessor dans Ai_Trading/app/MLearning/data/CèneDataTrading/
    CSV_FILE = os.path.abspath(os.path.join(script_dir, "..", "data", "CèneDataTrading", "enriched_data.csv"))

    if not os.path.exists(CSV_FILE):
        logger.error(f"enriched_data.csv introuvable : {CSV_FILE}")
        logger.info("Lancer d'abord CryptoDataProcessor pour générer enriched_data.csv :")
        logger.info("python -m app.MLearning.preprocessing.CryptoDataProcessor --input \"app/MLearning/data/btc_15m_data_2018_to_2025 (1).csv\" --output \"app/MLearning/data/CèneDataTrading\"")
        return

    logger.info(f"Using Dataset: {CSV_FILE}")
    logger.info("Using Q-Labels as target for training and validation")
    pipeline = AdvancedDataPipeline(csv_path=CSV_FILE, lookback=192, batch_size=128)
    
    try:
        train_loader, val_loader, test_loader, input_size = pipeline.load_and_prep()
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return

    # Initialize Model
    logger.info(f"Initializing model with input_size={input_size}...")
    model = LSTM_Production_Model(input_size=input_size)
    
    # Initialize Trainer
    trainer = Trainer(model=model, patience=30, learning_rate=0.001, accumulation_steps=4)
    
    # Train
    trained_model = trainer.fit(train_loader, val_loader, epochs=100)
    
    # Save Model
    os.makedirs("models", exist_ok=True)
    torch.save(trained_model.state_dict(), "models/lstm_model.pth")
    joblib.dump(pipeline.scaler, "models/scaler.pkl")
    logger.info("Model saved to models/lstm_model.pth")
    logger.info("Scaler saved to models/scaler.pkl")
    
    # Quantize
    trainer.quantize_model("models/lstm_model_quantized.pth")

if __name__ == "__main__":
    main()
