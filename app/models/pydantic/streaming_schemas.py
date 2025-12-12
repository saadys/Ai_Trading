from pydantic import BaseModel
from typing import Optional

class StreamRequest(BaseModel):
    symbol: str = "BTCUSDT"
    interval: Optional[str] = "1m"

class StreamStopRequest(BaseModel):
    symbol: str = "BTCUSDT"
