import os
import pandas as pd
import numpy as np
import joblib
import argparse
import talib
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from typing import Tuple, List, Optional
from .LABELING import LABELING

class CryptoDataProcessor:    
    def __init__(self, 
                 lookback: int = 96, 
                 future_window: int = 4, 
                 scaler_path: str = "artifacts/scaler.pkl"):

        self.lookback = lookback
        self.future_window = future_window
        self.labeler = LABELING(future_window=future_window)
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

    def add_Seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:

        print("Engineering features...")
        data = df.copy()
                
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
            
            data['month_sin'] = np.sin(2 * np.pi * (months - 1) / 12)
            data['month_cos'] = np.cos(2 * np.pi * (months - 1) / 12)
            
        return data

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Calculating technical indicators (Production Parity)...")
        data = df.copy()
        
        closes = data['Close'].values.astype(float)
        highs = data['High'].values.astype(float)
        lows = data['Low'].values.astype(float)
        
        #  (EMA) 
        data['ema_20'] = talib.EMA(closes, timeperiod=20)
        data['ema_50'] = talib.EMA(closes, timeperiod=50)
        data['ema_200'] = talib.EMA(closes, timeperiod=200)
        
        #  (RSI) 
        data['rsi_14'] = talib.RSI(closes, timeperiod=14)
        
        #  (ATR) 
        data['atr_14'] = talib.ATR(highs, lows, closes, timeperiod=14)
        
        # MACD 
        macd, macd_signal, macd_hist = talib.MACD(
            closes, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        data['macd_line'] = macd
        data['macd_signal'] = macd_signal
        data['macd_hist'] = macd_hist
        
        return data

    def create_positional_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Creating Positional Context features...")
        data = df.copy()
        
        epsilon = 1e-9
        
        # 1. Log-Distances to EMAs (Price Position)
        data['dist_ema_20'] = np.log((data['Close'] + epsilon) / (data['ema_20'] + epsilon))
        data['dist_ema_50'] = np.log((data['Close'] + epsilon) / (data['ema_50'] + epsilon))
        # Handle potential NaNs in EMA200 by filling or just letting dropna handle it later
        data['dist_ema_200'] = np.log((data['Close'] + epsilon) / (data['ema_200'] + epsilon))
        
        # Normalized RSI
        data['rsi_norm'] = data['rsi_14'] / 100.0
        
        # Normalized ATR (Volatility Ratio)
        data['atr_ratio'] = data['atr_14'] / data['Close']
        
        # Normalized MACD
        data['macd_norm'] = data['macd_line'] / data['Close']
        data['macd_sig_norm'] = data['macd_signal'] / data['Close']
        data['macd_hist_norm'] = data['macd_hist'] / data['Close']
        
        return data

        #def calculate_q_labels(self, data: pd.DataFrame) -> pd.DataFrame:
        #    # Note: data should have the diff columns if that is what we want to rely on
        #    # The user code accessed 'Close_diff' etc.
        #    closes = data['Close_diff'].values
        #    highs = data['High_diff'].values
        #    lows = data['Low_diff'].values
        #    opens = data['Open_diff'].values
        #    
        #    # Check if Volume exists
        #    if 'Volume' in data.columns:
        #        volumes = data['Volume'].values
        #    else:
        #        volumes = np.zeros_like(closes)
    #
        #    q_standard = []
        #    q_vwap = []
        #    q_gap = []
        #    
        #    # Use self.future_window
        #    fw = self.future_window
        #    n = len(closes)
        #    
        #    for t in range(n - fw):
        #        f_highs = highs[t+1 : t+1+fw]
        #        f_lows = lows[t+1 : t+1+fw]
        #        f_closes = closes[t+1 : t+1+fw]
        #        f_opens = opens[t+1 : t+1+fw]
        #        f_volumes = volumes[t+1 : t+1+fw]
        #        
        #        final_close = closes[t+fw]
        #        
        #        # Label Q Standard
        #        HH = np.max(f_highs)
        #        LL = np.min(f_lows)
        #        
        #        if HH == LL:
        #            q_std = 0.5
        #        else:
        #            q_std = (final_close - LL) / (HH - LL)
        #            
        #        # Label Q VWAP (Volume Weighted) 
        #        total_vol = np.sum(f_volumes)
        #        if total_vol == 0:
        #             vwap_val = np.mean(f_closes) 
        #        else:
        #             vwap_val = np.sum(f_closes * f_volumes) / total_vol
        #             
        #        if HH == LL:
        #            q_v = 0.5
        #        else:
        #            q_v = (vwap_val - LL) / (HH - LL)
        #            
        #        # Label Q Gap-Adjusted
        #        HH_true = np.max(np.maximum(f_highs, f_opens))
        #        LL_true = np.min(np.minimum(f_lows, f_opens))
        #        
        #        if HH_true == LL_true:
        #            q_g = 0.5
        #        else:
        #            q_g = (final_close - LL_true) / (HH_true - LL_true)
        #            
        #        q_standard.append(q_std)
        #        q_vwap.append(q_v)
        #        q_gap.append(q_g)
        #    
        #    pad = [np.nan] * fw
        #    
        #    # We should append these to 'data'
        #    data['Label_Q_Standard'] = q_standard + pad
        #    data['Label_Q_VWAP'] = q_vwap + pad
        #    data['Label_Q_Gap'] = q_gap + pad
        #    
        #    return data
    
    def scale_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        print("Scaling features...")
        data = df.copy()
        
        # We focus on the NEW positional features + Seasonal
        features = [
            # Base Features
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff','Volume'

            # Positional / Context Features
            'dist_ema_20', 'dist_ema_50', 'dist_ema_200',
            'rsi_norm', 
            'atr_ratio',
            'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
            
            # Seasonal Features 
            'hour_sin', 'hour_cos', 
            'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos',
            
            # Volume Log
             'Volume_log'
        ]
        
        if 'Volume' in data.columns:
             data['Volume_log'] = np.log1p(data['Volume'])
        
        numeric_features = [f for f in features if f in data.columns]
        
        meta_features = ['Open time', 'Close time']
        available_meta = [f for f in meta_features if f in data.columns]
        
        print(f"Selected numeric features for scaling: {numeric_features}")
        print(f"Selected metadata features: {available_meta}")
        
        if numeric_features:
            data[numeric_features] = self.scaler.fit_transform(data[numeric_features])
        
        print(f"Saving scaler to {self.scaler_path}...")
        joblib.dump(self.scaler, self.scaler_path)
        
        final_columns = numeric_features + available_meta
        X_scaled = data[final_columns].values
        
        if 'Label_Q_Standard' in data.columns:
            y_labels = data['Label_Q_Standard'].values
        else:
            y_labels = np.zeros(len(data))
        
        return X_scaled, y_labels, final_columns

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
        
        bins = [-np.inf, 0.33, 0.66, np.inf]
        y_train_series = pd.Series(y_train_raw)
        
        train_classes = pd.cut(y_train_series, bins=bins, labels=[0, 1, 2])
        if train_classes.isna().any():
            train_classes = train_classes.fillna(1)
            
        train_classes = train_classes.astype(int)
        
        class_counts = train_classes.value_counts()
        min_class_count = class_counts.min()
        
        print(f"Class distribution before balancing: {class_counts.to_dict()}")
        print(f"Downsampling to {min_class_count} samples per class...")
        
        balanced_indices = []
        for cls in [0, 1, 2]:
            cls_indices = np.where(train_classes == cls)[0]
            if len(cls_indices) > 0:
                 count = min(len(cls_indices), min_class_count)
                 selected = np.random.choice(cls_indices, count, replace=False)
                 balanced_indices.append(selected)
            
        if balanced_indices:
            balanced_indices = np.concatenate(balanced_indices)
            np.random.shuffle(balanced_indices)
            
            X_train = X_train_raw[balanced_indices]
            y_train = y_train_raw[balanced_indices]
        else:
            X_train = X_train_raw
            y_train = y_train_raw
        
        return {
            "X_train": X_train, "y_train": y_train,
            "X_val": X_val, "y_val": y_val,
            "X_test": X_test, "y_test": y_test
        }

    def run_pipeline(self, input_path: str, output_dir: str):
        df = self.load_data(input_path)
        
        #Feature Engineering
        df = self.add_Seasonal_features(df)
        df = self.calculate_technical_indicators(df)
        df = self.create_positional_features(df)
        
        # Labeling
        df = self.labeler.calculate_q_labels(df)
        
        # Cleaning
        df_clean = df.dropna().reset_index(drop=True)
        print(f"Data shape after cleaning: {df_clean.shape}")
        
        # EXPORT FOR TRAINER (Crucial Step)
        # We save the enriched data here so trainer.py can load it with all features
        enriched_path = os.path.join(output_dir, "enriched_data.parquet")
        print(f"Saving enriched data to {enriched_path}...")
        df_clean.to_parquet(enriched_path)
        
        # Scaling
        X_scaled, y_labels, cols = self.scale_features(df_clean)
        
        # Sequencing
        X_seq, y_seq = self.create_sequences(X_scaled, y_labels)
        
        # Splitting
        splits = self.split_and_balance(X_seq, y_seq)
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"Saving processed data to {output_dir}...")
        for name, arr in splits.items():
            np.save(os.path.join(output_dir, f"{name}.npy"), arr)
            print(f"Saved {name}: {arr.shape}")
        
        joblib.dump(cols, os.path.join(output_dir, "feature_names.pkl"))
            
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
