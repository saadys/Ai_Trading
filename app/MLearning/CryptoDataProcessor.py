import os
import pandas as pd
import numpy as np
import joblib
import argparse
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from typing import Tuple, List, Optional

class CryptoDataProcessor:    
    def __init__(self, 
                 lookback: int = 96, 
                 future_window: int = 4, 
                 scaler_path: str = "artifacts/scaler.pkl"):

        self.lookback = lookback
        self.future_window = future_window
        self.scaler_path = scaler_path
        self.scaler = RobustScaler()
        self.feature_cols = []
        
        os.makedirs(os.path.dirname(self.scaler_path), exist_ok=True)

    def load_data(self, filepath: str) -> pd.DataFrame:
        print(f"Loading data from {filepath}...")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        data = pd.read_csv(filepath)
        
        for col in ['Open time', 'Close time']:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col])
            
        return data

    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:

        print("Engineering features...")
        data = df.copy()
        
        # 1. Price Differences
        
        data['Open_diff'] = data['Open'].diff()
        data['High_diff'] = data['High'].diff()
        data['Low_diff'] = data['Low'].diff()
        data['Close_diff'] = data['Close'].diff()
        
        if 'Open time' in data.columns:
            timestamps = data['Open time']
            hours = timestamps.dt.hour
            day_of_week = timestamps.dt.dayofweek
            months = timestamps.dt.month
            
            data['hour_sin'] = np.sin(2 * np.pi * hours / 24)
            data['hour_cos'] = np.cos(2 * np.pi * hours / 24)
            
            data['day_of_week_sin'] = np.sin(2 * np.pi * day_of_week / 7)
            data['day_of_week_cos'] = np.cos(2 * np.pi * day_of_week / 7)
            
            # Month (1-12)
            data['month_sin'] = np.sin(2 * np.pi * (months - 1) / 12)
            data['month_cos'] = np.cos(2 * np.pi * (months - 1) / 12)
            
        return data

    def calculate_q_label(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Generating Q-Labels...")
        data = df.copy()
        
        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values
        
        q_labels = []
        n = len(closes)
        fw = self.future_window
        
        for t in range(n - fw):
            # Window t+1 to t+fw
            future_highs = highs[t+1 : t+1+fw]
            future_lows = lows[t+1 : t+1+fw]
            future_close = closes[t+fw]
            
            HH = np.max(future_highs)
            LL = np.min(future_lows)
            
            if HH == LL:
                q = 0.5
            else:
                q = (future_close - LL) / (HH - LL)
            q_labels.append(q)
            
        # Pad the end with NaNs to match length
        q_labels = np.array(q_labels + [np.nan] * fw)
        data['Label_Q'] = q_labels
        
        return data

    def scale_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        print("Scaling features...")
        data = df.copy()
        
        features = [
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff', 'Volume',
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos'
        ]
        
        available_features = [f for f in features if f in data.columns]
        if 'Volume' in data.columns:
            data['Volume'] = np.log1p(data['Volume'])
            
        data[available_features] = self.scaler.fit_transform(data[available_features])
        
        print(f"Saving scaler to {self.scaler_path}...")
        joblib.dump(self.scaler, self.scaler_path)
        
        X_scaled = data[available_features].values
        y_labels = data['Label_Q'].values
        
        return X_scaled, y_labels, available_features

    def create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        print(f"Creating sequences (lookback={self.lookback})...")
        X_out, y_out = [], []
        
        for i in range(self.lookback, len(X)):
            X_out.append(X[i-self.lookback : i])
            y_out.append(y[i])
            
        return np.array(X_out), np.array(y_out)

    def split_and_balance(self, X: np.ndarray, y: np.ndarray) -> dict:
        print("Splitting and balancing data...")
        total = len(X)
        train_idx = int(total * 0.80)
        val_idx = int(total * 0.90)
        
        X_train_raw = X[:train_idx]
        y_train_raw = y[:train_idx]
        
        X_val = X[train_idx:val_idx]
        y_val = y[train_idx:val_idx]
        
        X_test = X[val_idx:]
        y_test = y[val_idx:]
        
        # Balancing Logic (Notebook style: Binning -> Downsampling)
        # Bins: <0.33, 0.33-0.66, >0.66
        bins = [-np.inf, 0.33, 0.66, np.inf]
        y_train_series = pd.Series(y_train_raw)
        train_classes = pd.cut(y_train_series, bins=bins, labels=[0, 1, 2]).astype(int)
        
        class_counts = train_classes.value_counts()
        min_class_count = class_counts.min()
        
        print(f"Class distribution before balancing: {class_counts.to_dict()}")
        print(f"Downsampling to {min_class_count} samples per class...")
        
        balanced_indices = []
        for cls in [0, 1, 2]:
            cls_indices = np.where(train_classes == cls)[0]
            selected = np.random.choice(cls_indices, min_class_count, replace=False)
            balanced_indices.append(selected)
            
        balanced_indices = np.concatenate(balanced_indices)
        np.random.shuffle(balanced_indices)
        
        X_train = X_train_raw[balanced_indices]
        y_train = y_train_raw[balanced_indices]
        
        return {
            "X_train": X_train, "y_train": y_train,
            "X_val": X_val, "y_val": y_val,
            "X_test": X_test, "y_test": y_test
        }

    def run_pipeline(self, input_path: str, output_dir: str):
        df = self.load_data(input_path)
        
        df = self.add_technical_features(df)
        
        df = self.calculate_q_label(df)
        
        df_clean = df.dropna().reset_index(drop=True)
        print(f"Data shape after cleaning: {df_clean.shape}")
        
        X_scaled, y_labels, cols = self.scale_features(df_clean)
        
        X_seq, y_seq = self.create_sequences(X_scaled, y_labels)
        
        splits = self.split_and_balance(X_seq, y_seq)
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"Saving processed data to {output_dir}...")
        for name, arr in splits.items():
            np.save(os.path.join(output_dir, f"{name}.npy"), arr)
            print(f"Saved {name}: {arr.shape}")
            
        print("Pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto Data Preprocessing Pipeline")
    parser.add_argument("--input", type=str, default="data/raw/BTCUSDT.csv", help="Path to raw CSV")
    parser.add_argument("--output", type=str, default="data/processed", help="Output directory")
    args = parser.parse_args()
    
    # Adjust artifact path relative to this script
    pipeline = CryptoDataProcessor(scaler_path="artifacts/scaler.pkl")
    
    if os.path.exists(args.input):
        pipeline.run_pipeline(args.input, args.output)
    else:
        print(f"Input file not found at {args.input}. Please provide a valid path.")
