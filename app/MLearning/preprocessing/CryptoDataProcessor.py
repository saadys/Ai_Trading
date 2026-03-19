import os
import pandas as pd
import numpy as np
import argparse
import logging
import talib
from vmdpy import VMD
from .LABELING import LABELING

logger = logging.getLogger(__name__)

MODEL_FEATURES = [
    # 14 colonnes scalées
    'Open_diff', 'High_diff', 'Low_diff', 'Close_diff',
    'dist_ema_50', 'dist_ema_200',
    'atr_ratio',
    'macd_norm', 'macd_sig_norm', 'macd_hist_norm',
    'Volume_log',
    'VMD_Mode1_diff', 'VMD_Mode2', 'VMD_Mode3',
    # déjà normalisées
    'hour_sin', 'hour_cos',
    'day_of_week_sin', 'day_of_week_cos',
    'month_sin', 'month_cos',
    'rsi_norm',
]


class CryptoDataProcessor:
    def __init__(self,
                 lookback: int = 192,
                 future_window: int = 4):

        self.lookback = lookback
        self.future_window = future_window
        self.labeler = LABELING(future_window=future_window)

    def load_data(self, filepath: str) -> pd.DataFrame:
        logger.info(f"Loading data from {filepath}...")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        data = pd.read_csv(filepath)

        # Garder uniquement les colonnes brutes nécessaires
        keep_cols = [c for c in ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume'] if c in data.columns]
        data = data[keep_cols].copy()

        if 'Open time' in data.columns:
            data['Open time'] = pd.to_datetime(data['Open time'])
            data = (data
                    .sort_values('Open time')
                    .drop_duplicates(subset='Open time')
                    .reset_index(drop=True))

        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data.columns:
                data[col] = data[col].astype(float)

        logger.info(f"Données chargées : {len(data)} bougies.")
        return data

    def add_Seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Engineering features...")
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
        logger.info("Calculating technical indicators (Production Parity)...")
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
        logger.info("Creating positional & volume features...")
        data = df.copy()
        
        epsilon = 1e-9
        
        # Log-distances aux EMAs (normalisation scale-invariante par rapport au prix)
        data['dist_ema_20'] = np.log((data['Close'] + epsilon) / (data['ema_20'] + epsilon))
        data['dist_ema_50'] = np.log((data['Close'] + epsilon) / (data['ema_50'] + epsilon))
        data['dist_ema_200'] = np.log((data['Close'] + epsilon) / (data['ema_200'] + epsilon))
        
        data['rsi_norm'] = data['rsi_14'] / 100.0
        
        # Volatilité relative
        data['atr_ratio'] = data['atr_14'] / data['Close']
        
        # MACD normalisé par le prix (scale-invariant)
        data['macd_norm'] = data['macd_line'] / data['Close']
        data['macd_sig_norm'] = data['macd_signal'] / data['Close']
        data['macd_hist_norm'] = data['macd_hist'] / data['Close']
        
        # Volume log (compresse les spikes extrêmes)
        data['Volume_log'] = np.log1p(data['Volume'])

        return data

    def apply_vmd(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Applying VMD decomposition...")
        data = df.copy()

        closes = data['Close'].values
        alpha = 2000   # contrainte de bande passante
        tau = 0.       # tolérance au bruit
        K = 3          # 3 modes : tendance, oscillations moyennes, oscillations rapides
        DC = 0
        init = 1
        tol = 1e-7

        try:
            u, u_hat, omega = VMD(closes, alpha, tau, K, DC, init, tol)

            target_len = len(data)

            def _align_mode_length(mode: np.ndarray, n: int) -> np.ndarray:
                mode = np.asarray(mode, dtype=float).reshape(-1)
                m = len(mode)
                if m == n:
                    return mode
                if m < n:
                    pad_count = n - m
                    if m == 0:
                        return np.zeros(n, dtype=float)
                    return np.pad(mode, (pad_count, 0), mode='edge')
                return mode[-n:]

            mode1 = _align_mode_length(u[0, :], target_len)
            mode2 = _align_mode_length(u[1, :], target_len)
            mode3 = _align_mode_length(u[2, :], target_len)

            data['VMD_Mode1'] = mode1
            data['VMD_Mode2'] = mode2
            data['VMD_Mode3'] = mode3

            # Mode1 = tendance longue (non-stationnaire) → diff pour la stationnariser
            data['VMD_Mode1_diff'] = data['VMD_Mode1'].diff()
        except Exception as e:
            logger.exception(f"[CryptoDataProcessor] Erreur VMD : {e} — fallback à zéro.")
            data['VMD_Mode1_diff'] = 0.0
            data['VMD_Mode2'] = 0.0
            data['VMD_Mode3'] = 0.0

        return data

    def run_pipeline(self, input_path: str, output_dir: str):
        df = self.load_data(input_path)

        # 2. Feature engineering
        df = self.add_Seasonal_features(df)
        df = self.calculate_technical_indicators(df)
        df = self.create_positional_features(df)
        df = self.apply_vmd(df)

        # 3. Labeling — Target = Label_Q_Standard
        df = self.labeler.calculate_q_labels(df)
        df = df.rename(columns={'Label_Q_Standard': 'Target'})

        # 4. Nettoyage final (NaN dus aux indicateurs + future window du label)
        df_clean = df.dropna().reset_index(drop=True)
        logger.info(f"Shape après nettoyage : {df_clean.shape}")

        # 5. Vérification que toutes les features et la target sont présentes
        missing = [c for c in MODEL_FEATURES + ['Target'] if c not in df_clean.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes dans le dataset enrichi : {missing}")

        # 6. Export CSV — trainer.py prend ce fichier en entrée
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "enriched_data.csv")
        df_clean.to_csv(output_path, index=False)
        logger.info(f"Dataset enrichi sauvegardé : {output_path}")
        logger.info(f"Colonnes exportées ({len(df_clean.columns)}) : {list(df_clean.columns)}")
        logger.info("Pipeline terminé avec succès.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    default_input = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "btc_15m_data_2018_to_2025 (1).csv")
    )
    default_output = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "CèneDataTrading")
    )

    parser = argparse.ArgumentParser(description="Crypto Data Preprocessing Pipeline")
    parser.add_argument("--input", type=str, default=default_input, help="Chemin vers le CSV brut Binance")
    parser.add_argument("--output", type=str, default=default_output, help="Dossier de sortie du dataset enrichi")
    args = parser.parse_args()

    pipeline = CryptoDataProcessor()

    if os.path.exists(args.input):
        pipeline.run_pipeline(args.input, args.output)
    else:
        logger.error(f"Fichier introuvable : {args.input}")
