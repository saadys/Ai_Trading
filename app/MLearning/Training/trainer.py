import sys
import os
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


import mlflow

mlflow.set_tracking_uri("postgresql+psycopg2://postgres:saadys@localhost:5432/mlflow_db")
mlflow.set_experiment("Model LSTM V1")
mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)


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
                print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            print(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
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
        self.criterion = nn.HuberLoss(delta=1.0)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.learning_rate = learning_rate
        self.patience = patience
        self.early_stopping = EarlyStopping(patience=patience, verbose=True)
        self.accumulation_steps = accumulation_steps
        self.model_info = model_info

    def fit(self, 
            train_loader: DataLoader, 
            val_loader: DataLoader, 
            epochs: int = 100) -> nn.Module:
        
        print(f"Starting training on {self.device} for {epochs} epochs...")
        
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
                        self.optimizer.step()
                        self.optimizer.zero_grad()
                    
                    running_loss += loss.item() * X_batch.size(0) * self.accumulation_steps
                
                if (i + 1) % self.accumulation_steps != 0:
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                
                epoch_train_loss = running_loss / len(train_loader.dataset)
                train_losses.append(epoch_train_loss)
                
                self.model.eval()
                val_running_loss = 0.0
                
                # Metric Accumulators
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
                        
                        # Store for metrics
                        all_preds.append(outputs.cpu().numpy())
                        all_targets.append(y_val.cpu().numpy())
                
                all_preds = np.concatenate(all_preds).flatten()
                all_targets = np.concatenate(all_targets).flatten()
                
                epoch_val_loss = val_running_loss / len(val_loader.dataset)
                val_losses.append(epoch_val_loss)

                # Custom Metrics
                mae = np.mean(np.abs(all_preds - all_targets))
                rmse = np.sqrt(np.mean((all_preds - all_targets)**2))
                # MAPE (Handle epsilon for division by zero)
                epsilon = 1e-8
                mape = np.mean(np.abs((all_targets - all_preds) / (all_targets + epsilon))) * 100
                
                # R2 Score
                ss_res = np.sum((all_targets - all_preds)**2)
                ss_tot = np.sum((all_targets - np.mean(all_targets))**2)
                r2_score = 1 - (ss_res / (ss_tot + epsilon))

                print(f'Epoch {epoch+1}/{epochs} | Train Loss: {epoch_train_loss:.6f} | Val Loss: {epoch_val_loss:.6f} | R2: {r2_score:.4f}')
                
                self.early_stopping(epoch_val_loss, self.model)
                
                if self.early_stopping.early_stop:
                    print("Early stopping triggered.")
                    break
            
                # Load best model
                if self.early_stopping.best_model_state:
                    self.model.load_state_dict(self.early_stopping.best_model_state)
                    print("Loaded best model state from early stopping checkpoint.")
                
                mlflow.log_metrics(
                    {
                        "train_loss": epoch_train_loss,
                        "val_loss": epoch_val_loss,
                        "MAE": mae,
                        "RMSE": rmse,
                        "MAPE": mape,
                        "R2_Score": r2_score
                    },
                    step=epoch
                )
                mlflow.pytorch.log_model(self.model, name=f"checkpoint_{epoch}")
                
            self.model_info = mlflow.pytorch.log_model(self.model, name="final_model")

                

        return self.model

    def quantize_model(self, save_path: str = "models/lstm_model_quantized.pth"):
        print("Applying Dynamic Quantization...")
        self.model.to('cpu')
        self.model.eval()
        
        quantized_model = torch.quantization.quantize_dynamic(
            self.model, {nn.LSTM, nn.Linear}, dtype=torch.qint8
        )
        
        print(f"Quantization complete. Saving to {save_path}...")
        torch.save(quantized_model.state_dict(), save_path)
        return quantized_model

class AdvancedDataPipeline:
    def __init__(self, parquet_path: str, lookback: int = 96, batch_size: int = 32):
        self.parquet_path = parquet_path
        self.lookback = lookback
        self.batch_size = batch_size
        self.scaler = RobustScaler()
        self.target_scaler = RobustScaler() 
        self.feature_cols = [
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff', 'Volume',
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos', 'VMD_Mode1', 'VMD_Mode2', 'VMD_Mode3'
        ]
        self.target_col = 'Label_Q_Standard'

    def load_and_prep(self) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
        print(f"Loading parquet from {self.parquet_path}...")
        try:
            df = pd.read_parquet(self.parquet_path)
        except Exception as e:
            print(f"Error reading parquet file: {e}")
            raise

        initial_len = len(df)
        df = df.dropna()
        dropped_len = len(df)
        print(f"Dropped {initial_len - dropped_len} row(s) containing NaNs.")
        
        if dropped_len == 0:
            raise ValueError("All data dropped! Check your data source.")

        missing_cols = [c for c in self.feature_cols if c not in df.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}. Ignoring them.")
            self.feature_cols = [c for c in self.feature_cols if c in df.columns]

        #Time Series Split
        n = len(df)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)

        # Split features into those needing scaling vs passthrough (cyclic)
        scale_cols = [
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff', 'Volume',
            'VMD_Mode1', 'VMD_Mode2', 'VMD_Mode3'
        ]
        passthrough_cols = [
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos'
        ]
        
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

        print("Fitting scalers on training data...")
        
        # Fit scaler on scale_cols
        X_train_scale_part = self.scaler.fit_transform(X_train_raw[scale_cols].values)
        X_val_scale_part = self.scaler.transform(X_val_raw[scale_cols].values)
        X_test_scale_part = self.scaler.transform(X_test_raw[scale_cols].values)
        
        # Get passthrough parts
        X_train_pass = X_train_raw[passthrough_cols].values
        X_val_pass = X_val_raw[passthrough_cols].values
        X_test_pass = X_test_raw[passthrough_cols].values
        
        # Concatenate back: Scaled + Passthrough
        X_train_final = np.hstack([X_train_scale_part, X_train_pass])
        X_val_final = np.hstack([X_val_scale_part, X_val_pass])
        X_test_final = np.hstack([X_test_scale_part, X_test_pass])
        
        # Scale Target
        # Since labels are now clean [0, 1], we do NOT need to scale or clip them.
        # This allows direct interpretation of predictions as Q-scores.
        y_train_scaled = y_train_raw.flatten()
        y_val_scaled = y_val_raw.flatten()
        y_test_scaled = y_test_raw.flatten()

        print("Target values are clean (0-1). No sealing/clipping applied.")

        X_train_seq, y_train_seq = self._create_sequences(X_train_final, y_train_scaled)
        X_val_seq, y_val_seq = self._create_sequences(X_val_final, y_val_scaled)
        X_test_seq, y_test_seq = self._create_sequences(X_test_final, y_test_scaled)

        print(f"Train seq: {X_train_seq.shape}, Val seq: {X_val_seq.shape}, Test seq: {X_test_seq.shape}")

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
        for i in range(len(X) - self.lookback):
            Xs.append(X[i:(i + self.lookback)])
            ys.append(y[i + self.lookback])
        return np.array(Xs), np.array(ys)

def main():
    PARQUET_FILE = os.path.join("Ai_Trading", "app", "MLearning", "MVP ML", "data", "data_final_with_vmd_features.parquet")
    
    if not os.path.exists(PARQUET_FILE):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        PARQUET_FILE = os.path.abspath(os.path.join(script_dir, "..", "MVP ML", "data", "data_final_with_vmd_features.parquet"))
    
    if not os.path.exists(PARQUET_FILE):
        print(f"Parquet file not found at {PARQUET_FILE}")
        print(f"Current Working Directory: {os.getcwd()}")
        return

    pipeline = AdvancedDataPipeline(parquet_path=PARQUET_FILE, lookback=96, batch_size=32)
    
    try:
        train_loader, val_loader, test_loader, input_size = pipeline.load_and_prep()
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return

    # Initialize Model
    print(f"Initializing model with input_size={input_size}...")
    model = LSTM_Production_Model(input_size=input_size)
    
    # Initialize Trainer
    trainer = Trainer(model=model, patience=10, learning_rate=0.001, accumulation_steps=4)
    
    # Train
    trained_model = trainer.fit(train_loader, val_loader, epochs=100)
    
    # Save Model
    os.makedirs("models", exist_ok=True)
    torch.save(trained_model.state_dict(), "models/lstm_model.pth")
    print("Model saved to models/lstm_model.pth")
    
    # Quantize
    trainer.quantize_model("models/lstm_model_quantized.pth")

if __name__ == "__main__":
    main()
