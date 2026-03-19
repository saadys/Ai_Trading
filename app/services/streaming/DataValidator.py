from  pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class DataValidator(BaseModel):
    symbol : str = Field(..., description="Le symbole de la paire, ex: BTCUSDT")
    open_time : datetime = Field(..., description="Timestamp d'ouverture de la bougie")
    open_price : Optional[float] = Field(..., alias="o")
    high_price : Optional[float] = Field(..., alias="h")
    low_price : Optional[float] = Field(..., alias="l")
    close_price : Optional[float] = Field(..., alias="c")
    volume : Optional[float] = Field(..., alias="v")
    close_time: datetime = Field(..., description="Timestamp de fermeture de la bougie")
    is_closed: bool = Field(..., description="Indique si la bougie est clôturée")
    
    model_config = ConfigDict(populate_by_name=True)
    