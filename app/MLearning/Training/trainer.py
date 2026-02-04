import sys
import os

# Fix OpenMP runtime error: initializing libiomp5md.dll, but found libiomp5md.dll already initialized
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

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
mlflow.set_experiment("Model LSTM V2")
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

class NewDataPipeline:
    def __init__(self, csv_path: str, lookback: int = 96, batch_size: int = 32):
        self.csv_path = csv_path
        self.lookback = lookback
        self.batch_size = batch_size
        
        # Exact Feature Mapping (Order matters for inference consistency)
        # Total Features: 21 (18 Base + 3 VMD)
        self.feature_cols = [
            # Price Dynamics (4)
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
            # Positional Context (7)
            'dist_ema_50', 'dist_ema_200', 'rsi_norm', 'atr_ratio', 
            'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
            # Seasonality (6)
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos',
            # Volume (1)
            'Volume_log',
            # VMD Modes (3)
            'VMD_Mode1', 'VMD_Mode2', 'VMD_Mode3'
        ]
        self.target_col = 'Target'

    def load_and_prep(self) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
        print(f"Loading final dataset from {self.csv_path}...")
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            raise

        # Check for missing features
        missing = [c for c in self.feature_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required features in CSV: {missing}")

        # Ensure Time is datetime for Gap Detection
        if 'Open time' not in df.columns:
             raise ValueError("'Open time' column required for gap detection.")
        
        df['Open time'] = pd.to_datetime(df['Open time'])
        df = df.sort_values('Open time').reset_index(drop=True)
        
        # 1. Integrity Check: Gap Detection
        # Calculate time diffs between rows
        time_diffs = df['Open time'].diff()
        # Standard interval is 15min. We flag anything > 16min as a gap.
        # This boolean mask marks the START of a new continuous block
        gap_mask = time_diffs > pd.Timedelta(minutes=16) 
        
        # Create 'Block ID' group by cumulative sum of gaps
        df['block_id'] = gap_mask.cumsum()
        n_blocks = df['block_id'].nunique()
        print(f"Gap Analysis: Found {n_blocks - 1} time gaps. Created {n_blocks} continuous blocks.")

        # 2. Extract Features and Target
        # Data is ALREADY SCALED in NewdataFinal.csv (RobustScaler applied previously).
        # We do NOT apply further scaling here to preserve distribution logic.
        
        # Prepare lists to hold sequences from ALL blocks
        X_all_seqs = []
        y_all_seqs = []
        
        print(f"Generating sequences (lookback={self.lookback})...")
        
        # Iterate over each continuous block to generate valid sequences without jumping gaps
        for block_id, block_data in df.groupby('block_id'):
            if len(block_data) <= self.lookback:
                continue # Skip blocks shorter than lookback window
                
            X_block = block_data[self.feature_cols].values
            y_block = block_data[self.target_col].values
            
            # Create sequences for this block
            Xs, ys = self._create_sequences(X_block, y_block)
            
            if len(Xs) > 0:
                X_all_seqs.append(Xs)
                y_all_seqs.append(ys)
        
        if not X_all_seqs:
            raise ValueError("No valid sequences generated! Check lookback vs data length.")
            
        # Concatenate all sequences from all blocks
        X_final = np.concatenate(X_all_seqs, axis=0)
        y_final = np.concatenate(y_all_seqs, axis=0).reshape(-1, 1)
        
        print(f"Total Sequences Generated: {len(X_final)}")
        print(f"Input Shape: {X_final.shape}") # (N, 96, 21)
        
        # 3. Time Series Split (80/10/10) - Resecting Time Order
        # Since X_final is ordered by time (blocks were processed in order), simple slicing works.
        n_samples = len(X_final)
        train_idx = int(n_samples * 0.8)
        val_idx = int(n_samples * 0.9)
        
        X_train = X_final[:train_idx]
        y_train = y_final[:train_idx]
        
        X_val = X_final[train_idx:val_idx]
        y_val = y_final[train_idx:val_idx]
        
        X_test = X_final[val_idx:]
        y_test = y_final[val_idx:]
        
        print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

        # 4. Create DataLoaders
        # Convert to PyTorch Tensors
        train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
        val_dataset = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
        test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True) # Shuffle Train samples
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        input_size = X_train.shape[2] # Should be 21
        return train_loader, val_loader, test_loader, input_size

    def _create_sequences(self, X, y):
        # Optimized sequence generation using sliding window view (if possible) or list comp
        Xs, ys = [], []
        # Need lookback steps + 1 target step
        for i in range(len(X) - self.lookback):
            Xs.append(X[i:(i + self.lookback)])
            ys.append(y[i + self.lookback]) # Target is the NEXT candle after sequence ? Or current?
            # Standard: predict T based on T-Lookback...T-1. 
            # If y aligns with X, y[i+lookback] is the target for window i..i+lookback
        return np.array(Xs), np.array(ys)

def main():
    # New Dataset Path
    CSV_FILE = os.path.join("Ai_Trading", "data", "NewdataFinal.csv")
    
    if not os.path.exists(CSV_FILE):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Try to resolve relative to script
        CSV_FILE = os.path.abspath(os.path.join(script_dir, "../../../data/NewdataFinal.csv"))
    
    if not os.path.exists(CSV_FILE):
        print(f"CRITICAL: Dataset not found at {CSV_FILE}")
        return

    # Use NewDataPipeline with 21 features
    pipeline = NewDataPipeline(csv_path=CSV_FILE, lookback=96, batch_size=32)
    
    try:
        train_loader, val_loader, test_loader, input_size = pipeline.load_and_prep()
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return
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
