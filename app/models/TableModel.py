
from app.models.BaseDataModel import BaseDataModel
from app.models.db_schemas.mini_Trading.schemas.MarketData import MarketData
from typing import List
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

class TableModel(BaseDataModel):
    def __init__(self,database_client):
        super().__init__(database_client=database_client)

    
    async def save_ohlcv_batch(self, message: List[dict]):
        async with self.database_client() as session:
            async with session.begin():
                ohlcv_batch = []
                for payload in message:
                    # Convert string dates to datetime objects if they are strings
                    if isinstance(payload.get('open_time'), str):
                        try:
                            payload['open_time'] = datetime.fromisoformat(payload['open_time'].replace('Z', '+00:00'))
                        except ValueError:
                            pass
                            
                    if isinstance(payload.get('close_time'), str):
                        try:
                            payload['close_time'] = datetime.fromisoformat(payload['close_time'].replace('Z', '+00:00'))
                        except ValueError:
                            pass

                    ohlcv_batch.append(MarketData(**payload))
                session.add_all(ohlcv_batch)
        return ohlcv_batch
