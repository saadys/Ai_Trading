import pandas as pd
import numpy as np

class LABELING:
    def __init__(self, future_window: int = 4):
        
        self.future_window = future_window
    
    def calculate_q_labels(self, data: pd.DataFrame) -> pd.DataFrame:
        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values
        opens = data['Open'].values
        
        # Check if Volume exists
        if 'Volume' in data.columns:
            volumes = data['Volume'].values
        else:
            volumes = np.zeros_like(closes)

        q_standard = []
        q_vwap = []
        q_gap = []
        
        # Use self.future_window
        fw = self.future_window
        n = len(closes)
        
        for t in range(n - fw):
            f_highs = highs[t+1 : t+1+fw]
            f_lows = lows[t+1 : t+1+fw]
            f_closes = closes[t+1 : t+1+fw]
            f_opens = opens[t+1 : t+1+fw]
            f_volumes = volumes[t+1 : t+1+fw]
            
            final_close = closes[t+fw]
            
            # Label Q Standard
            HH = np.max(f_highs)
            LL = np.min(f_lows)
            
            if HH == LL:
                q_std = 0.5
            else:
                q_std = (final_close - LL) / (HH - LL)
                
            # Label Q VWAP (Volume Weighted) 
            total_vol = np.sum(f_volumes)
            if total_vol == 0:
                 vwap_val = np.mean(f_closes) 
            else:
                 vwap_val = np.sum(f_closes * f_volumes) / total_vol
                 
            if HH == LL:
                q_v = 0.5
            else:
                q_v = (vwap_val - LL) / (HH - LL)
                
            # Label Q Gap-Adjusted
            HH_true = np.max(np.maximum(f_highs, f_opens))
            LL_true = np.min(np.minimum(f_lows, f_opens))
            
            if HH_true == LL_true:
                q_g = 0.5
            else:
                q_g = (final_close - LL_true) / (HH_true - LL_true)
                
            q_standard.append(q_std)
            q_vwap.append(q_v)
            q_gap.append(q_g)
        
        pad = [np.nan] * fw
        
        # We should append these to 'data'
        data['Label_Q_Standard'] = q_standard + pad
        data['Label_Q_VWAP'] = q_vwap + pad
        data['Label_Q_Gap'] = q_gap + pad
        
        return data