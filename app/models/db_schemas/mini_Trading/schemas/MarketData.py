from sqlalchemy import Column, Integer, String, Float, DateTime, func, Boolean
from .Base_Trading import SQLAlchemyBase
from datetime import datetime
from sqlalchemy.orm import relationship

class MarketData(SQLAlchemyBase):
    __tablename__ = 'OHLCV'

    id_OHLCV = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    open_time = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    close_time = Column(DateTime(timezone=True), nullable=False, index=True)
    is_closed = Column(Boolean, nullable=False)
    exchange_name = Column(String, nullable=True)

    # Relationships
    indicators = relationship("IndicatorTechnique", back_populates="ohlcv", cascade="all, delete-orphan")
