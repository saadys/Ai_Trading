from app.models.BaseDataModel import BaseDataModel
from app.models.db_schemas.mini_Trading.schemas.MarketData import MarketData
from app.models.db_schemas.mini_Trading.schemas.MLPrediction import MLPrediction
from app.models.db_schemas.mini_Trading.schemas.IndicatorTechnique import IndicatorTechnique


from typing import List
from datetime import datetime
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

logger = logging.getLogger(__name__)

class TableModel(BaseDataModel):
    def __init__(self,database_client):
        super().__init__(database_client=database_client)

    @staticmethod
    def _parse_datetime(value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value

    async def save_ml_prediction_batch(self, message: List[dict]):
        async with self.database_client() as session:
            async with session.begin():
                pred_batch = []
                for payload in message:
                    payload['timestamp'] = self._parse_datetime(payload.get('timestamp'))
                    pred_batch.append(MLPrediction(**payload))
                session.add_all(pred_batch)
        return pred_batch


    
    async def save_ohlcv_batch(self, message: List[dict]):
        async with self.database_client() as session:
            async with session.begin():
                ohlcv_batch = []
                for payload in message:
                    payload['open_time'] = self._parse_datetime(payload.get('open_time'))
                    payload['close_time'] = self._parse_datetime(payload.get('close_time'))
                    ohlcv_batch.append(MarketData(**payload))
                session.add_all(ohlcv_batch)
        return ohlcv_batch

    async def save_indicator_batch(self, message: List[dict]):
        valid_payloads = []

        for payload in message:
            mapped_payload = {
                'OHLCV_ID': payload.get('OHLCV_ID') or payload.get('ohlcv_id') or payload.get('id_OHLCV'),
                'timestamp': self._parse_datetime(payload.get('timestamp')),
                'symbol': payload.get('symbol'),
                'RSI': payload.get('RSI') if payload.get('RSI') is not None else payload.get('rsi_14'),
                'MACD': payload.get('MACD') if payload.get('MACD') is not None else payload.get('macd_line'),
                'MA': payload.get('MA') if payload.get('MA') is not None else payload.get('ema_20'),
                'VWAP': payload.get('VWAP') if payload.get('VWAP') is not None else payload.get('vwap'),
                'BollingerBands': payload.get('BollingerBands') if payload.get('BollingerBands') is not None else payload.get('bollinger_bands'),
            }

            required = ('OHLCV_ID', 'symbol', 'RSI', 'MACD', 'MA', 'VWAP', 'BollingerBands')
            if any(mapped_payload.get(key) is None for key in required):
                logger.warning(
                    "Indicator payload skipped: missing required fields (%s)",
                    {key: mapped_payload.get(key) for key in required},
                )
                continue

            valid_payloads.append(mapped_payload)

        if not valid_payloads:
            return []

        async with self.database_client() as session:
            async with session.begin():
                indicator_batch = [IndicatorTechnique(**payload) for payload in valid_payloads]
                session.add_all(indicator_batch)

        return indicator_batch

    async def save_data_news_batch(self, message: List[dict]):
        try:
            from app.models.db_schemas.mini_Trading.schemas.NewsData import NewsData
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "NewsData model is missing. Add NewsData SQLAlchemy schema and Alembic migration before persisting Data_News."
            ) from exc

        news_batch = []
        for payload in message:
            normalized = dict(payload)
            normalized['timestamp'] = self._parse_datetime(normalized.get('timestamp'))
            normalized['pub_date'] = self._parse_datetime(normalized.get('pub_date'))

            try:
                news_batch.append(NewsData(**normalized))
            except Exception:
                logger.warning("Invalid Data_News payload skipped: %s", normalized)

        if not news_batch:
            return []

        async with self.database_client() as session:
            async with session.begin():
                session.add_all(news_batch)

        return news_batch    

