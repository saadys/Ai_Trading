import os
import pandas as pd
import numpy as np
import joblib
import talib
from typing import Tuple, List, Optional
from datetime import datetime
from vmdpy import VMD

class OnlineFeatureEngineer:
    def __init__(self, 
                 buffer_size: int = 400, 
                 lookback: int = 192,
                 scaler_path: str = None):
        
        self.buffer_size = buffer_size
        self.lookback = lookback
        
        if scaler_path is None:
            self.scaler_path = self._resolve_scaler_path()
        else:
            self.scaler_path = scaler_path
            
        print(f"[OnlineFeatureEngineer] Chargement du scaler depuis : {self.scaler_path}")
        try:
            self.scaler = joblib.load(self.scaler_path)
            self.scaler_error = None
        except Exception as e:
            self.scaler = None
            self.scaler_error = str(e)
            print(f"[OnlineFeatureEngineer] Scaler indisponible, passage en mode dégradé: {e}")

        self.buffer = []

        self.raw_cols = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.scale_cols = [
            # 14 features scalées par RobustScaler
            'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
            'dist_ema_50', 'dist_ema_200',
            'atr_ratio',
            'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
            'Volume_log',
            'VMD_Mode1_diff', 'VMD_Mode2', 'VMD_Mode3',
            # 7 features passthrough 
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos',
            'rsi_norm',
        ]

    @staticmethod
    def _resolve_scaler_path() -> str:
        current_dir = os.path.dirname(__file__)
        candidates = [
            os.path.join(current_dir, "artifacts", "scaler.pkl"),
            os.path.abspath(os.path.join(current_dir, "..", "..", "..", "models", "scaler.pkl")),
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        return candidates[0]
        
    def add_historical_data(self, history: List[dict]):
        for row in history:
            self.add_candle(row)

    def add_candle(self, candle: dict):
        # Mapping et harmonisation des clés (si camelCase ou snake_case)
        formatted_candle = {
            'Open time': pd.to_datetime(candle.get('open_time') or candle.get('Open time')),
            'Open': float(candle.get('open') or candle.get('Open', 0.0)),
            'High': float(candle.get('high') or candle.get('High', 0.0)),
            'Low': float(candle.get('low') or candle.get('Low', 0.0)),
            'Close': float(candle.get('close') or candle.get('Close', 0.0)),
            'Volume': float(candle.get('volume') or candle.get('Volume', 0.0)),
        }
        
        self.buffer.append(formatted_candle)
        
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

    def is_ready(self) -> bool:
        return len(self.buffer) >= self.lookback + 200 

    def get_health(self) -> dict:
        return {
            "scaler_loaded": self.scaler is not None,
            "scaler_path": self.scaler_path,
            "scaler_error": self.scaler_error,
            "buffer_size": len(self.buffer),
            "lookback": self.lookback,
            "buffer_ready": self.is_ready()
        }

    def _apply_vmd(self, df: pd.DataFrame) -> pd.DataFrame:
        closes = df['Close'].values
        alpha = 2000       # moderate bandwidth constraint
        tau = 0.           # noise-tolerance (no strict fidelity enforcement)
        K = 3              # 3 modes
        DC = 0             # no DC part imposed
        init = 1           # initialize omegas uniformly
        tol = 1e-7
        
        try:
            u, u_hat, omega = VMD(closes, alpha, tau, K, DC, init, tol)
            df['VMD_Mode1'] = u[0, :]
            df['VMD_Mode2'] = u[1, :]
            df['VMD_Mode3'] = u[2, :]
            df['VMD_Mode1_diff'] = df['VMD_Mode1'].diff()
        except Exception as e:
            print(f"[OnlineFeatureEngineer] Erreur VMD: {e}")
            df['VMD_Mode1_diff'] = 0.0
            df['VMD_Mode2'] = 0.0
            df['VMD_Mode3'] = 0.0
            
        return df

    def get_features(self) -> Optional[np.ndarray]:
        if not self.is_ready():
            print(f"[OnlineFeatureEngineer] Buffer insuffisant: {len(self.buffer)}/{self.lookback + 200}")
            return None

        if self.scaler is None:
            print("[OnlineFeatureEngineer] Scaler indisponible: features ML non générées (mode dégradé).")
            return None
            
        # 1. Convertir le buffer en DataFrame
        df = pd.DataFrame(self.buffer)
        
        # 2. Base Features & Diffs
        df['Open_diff'] = df['Open'].diff()
        df['High_diff'] = df['High'].diff()
        df['Low_diff'] = df['Low'].diff()
        df['Close_diff'] = df['Close'].diff()
        
        # 3. Time Features
        timestamps = df['Open time']
        hours = timestamps.dt.hour
        day_of_week = timestamps.dt.dayofweek
        months = timestamps.dt.month
        
        df['hour_sin'] = np.sin(2 * np.pi * hours / 24)
        df['hour_cos'] = np.cos(2 * np.pi * hours / 24)
        df['day_of_week_sin'] = np.sin(2 * np.pi * day_of_week / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * day_of_week / 7)
        df['month_sin'] = np.sin(2 * np.pi * (months - 1) / 12)
        df['month_cos'] = np.cos(2 * np.pi * (months - 1) / 12)
        
        # 4. Technical Indicators
        closes = df['Close'].values.astype(float)
        highs = df['High'].values.astype(float)
        lows = df['Low'].values.astype(float)
        
        df['ema_20'] = talib.EMA(closes, timeperiod=20)
        df['ema_50'] = talib.EMA(closes, timeperiod=50)
        df['ema_200'] = talib.EMA(closes, timeperiod=200)
        
        df['rsi_14'] = talib.RSI(closes, timeperiod=14)
        df['atr_14'] = talib.ATR(highs, lows, closes, timeperiod=14)
        
        macd, macd_signal, macd_hist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd_line'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist
        
        # 5. Positional Features
        epsilon = 1e-9
        df['dist_ema_20'] = np.log((df['Close'] + epsilon) / (df['ema_20'] + epsilon))
        df['dist_ema_50'] = np.log((df['Close'] + epsilon) / (df['ema_50'] + epsilon))
        df['dist_ema_200'] = np.log((df['Close'] + epsilon) / (df['ema_200'] + epsilon))
        
        df['rsi_norm'] = df['rsi_14'] / 100.0
        df['atr_ratio'] = df['atr_14'] / df['Close']
        df['macd_norm'] = df['macd_line'] / df['Close']
        df['macd_sig_norm'] = df['macd_signal'] / df['Close']
        df['macd_hist_norm'] = df['macd_hist'] / df['Close']
        
        # 6. Volume
        df['Volume_log'] = np.log1p(df['Volume'])
        
        # 7. VMD
        df = self._apply_vmd(df)
        
        # 8. Extraire les N dernières lignes (Lookback)
        df_recent = df.iloc[-self.lookback:].copy()
        
        # S'assurer qu'il ne reste pas de NaN sur les dernières lignes (fallback sécurité)
        df_recent.fillna(method='bfill', inplace=True)
        df_recent.fillna(0.0, inplace=True)
        
        # 9. Sélectionner les colonnes exactes attendues par le StandardScaler/RobustScaler
        try:
            # Les 14 variables scalées et 7 variables non scalées telles que définies dans l'entrainement
            scale_cols_exact = [
                'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
                'dist_ema_50', 'dist_ema_200',
                'atr_ratio',
                'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
                'Volume_log',
                'VMD_Mode1_diff', 'VMD_Mode2', 'VMD_Mode3'
            ]
            
            X_scale_part = self.scaler.transform(df_recent[scale_cols_exact].values)
            passthrough_cols = [
                'hour_sin', 'hour_cos',
                'day_of_week_sin', 'day_of_week_cos',
                'month_sin', 'month_cos',
                'rsi_norm'
            ]
            
            X_pass_part = df_recent[passthrough_cols].values
            
            X_final = np.hstack([X_scale_part, X_pass_part])
            
            X_tensor_ready = X_final.reshape(1, self.lookback, 21)
            return X_tensor_ready
            
        except Exception as e:
            print(f"[OnlineFeatureEngineer] Erreur lors de la transformation/scaling: {e}")
            return None
