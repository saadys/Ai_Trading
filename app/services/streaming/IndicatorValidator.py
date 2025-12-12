from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class IndicatorValidator(BaseModel):
    """
    Validateur strict pour les indicateurs techniques.
    Empêche les valeurs aberrantes de corrompre la DB ou la stratégie.
    """
    symbol: str = Field(..., description="Symbole de la paire (ex: BTCUSDT)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # --- Indicateurs de Tendance (EMA) ---
    ema_20: Optional[float] = Field(None, gt=0, description="EMA 20 périodes")
    ema_50: Optional[float] = Field(None, gt=0, description="EMA 50 périodes")
    ema_200: Optional[float] = Field(None, gt=0, description="EMA 200 périodes")
    
    # --- Indicateurs de Momentum (RSI) ---
    rsi_14: Optional[float] = Field(None, ge=0, le=100, description="RSI 14 (doit être entre 0 et 100)")
    
    # --- Indicateurs de Volatilité (ATR) ---
    atr_14: Optional[float] = Field(None, gt=0, description="ATR 14 (doit être positif)")
    
    # --- Indicateurs de MACD ---
    macd_line: Optional[float] = Field(None, description="Ligne MACD")
    macd_signal: Optional[float] = Field(None, description="Ligne Signal")
    macd_hist: Optional[float] = Field(None, description="Histogramme MACD")

    @validator('rsi_14')
    def validate_rsi(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError(f"RSI invalide: {v}. Doit être entre 0 et 100.")
        return v
