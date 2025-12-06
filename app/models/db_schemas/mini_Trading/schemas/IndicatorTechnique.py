from sqlalchemy import Column, String, Integer,Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .Base_Trading import SQLAlchemyBase
from datetime import datetime

class IndicatorTechnique(SQLAlchemyBase):

    __tablename__ = 'IndicatorTechnique'
    
    id_IndiTech = Column(Integer, primary_key=True)
    OHLCV_ID = Column(Integer, nullable=False, ForeignKey='OHLCV.id_OHLCV')
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, default=datetime.utcnow)
    symbol = Column(String, nullable=False)
    RSI = Column(Float, nullable=False)
    MACD = Column(Float, nullable=False)
    MA = Column(Float, nullable=False)
    VWAP = Column(Float, nullable=False)
    BollingerBands  = Column(Float, nullable=False)

    ohlcv = relationship("OHLCV", back_populates="indicators") 

    