import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.services.streaming.QueueManager import QueueManager
from app.services.streaming.DataValidator import DataValidator
from app.services.streaming.IndicatorValidator import IndicatorValidator
from app.models.pydantic.SentimentValidator import SentimentValidator
from app.core.Logger import Logger, logger
from pydantic import ValidationError
from datetime import datetime
logger = Logger()

class ContextAggregator:
    def __init__(self,queuemanager: QueueManager):
        self.queue = queuemanager
        # État en mémoire pour accumuler les données
        self.state = {
            "OHLCV": {},
            "sentiment": {},
            "indicators": {},
            "ml_prediction": {},
            "account": {}
        }
        

    async def start(self):
        if not self.queue.connection or self.queue.connection.is_closed:
            logger.info("Connecting to RabbitMQ")
            await self.queue.connect()

        logger.info("Setting up broker")
        await self.queue.setup_broker()

        await self.queue.consume(
            queue_name='context_aggregator_queue',
            on_message_callback=self.process_message
        )
        logger.info("ContextAggregator started and listening.") 

    async def process_message(self, message: dict):
        if not message:
            logger.warning("Received empty message")
            return None
        
        payload = message.get("payload")
        logger.info(f"Received message of type: {message.get('type')}")

        if message.get("type") == "OHLCV":
            logger.info(f"Received OHLCV data")
            await self._process_ohlcv(payload)

        elif message.get("type") == "INDICATOR":
            logger.info(f"Received INDICATOR data")
            await self._process_indicator(payload)
            
        elif message.get("type") == "Sentiment":
            logger.info(f"Received Sentiment data")
            await self._process_sentiment(payload)

        elif message.get("type") == "ml_prediction":
            logger.info(f"Received ML Prediction data")
            await self._process_ml_pred(payload)
        elif message.get("type") == "account":
            await self._process_account(payload)


    async def _process_ohlcv(self, payload: dict):
        try:
            if not payload:
                logger.warning("Payload OHLCV vide")
                return None
            
            # Valider le payload avec la class DataValidator
            validated_data = DataValidator(**payload)
            
            self.state["OHLCV"] = {
                "symbol": validated_data.symbol,
                "open": validated_data.open_price,
                "high": validated_data.high_price,
                "low": validated_data.low_price,
                "close": validated_data.close_price,
                "volume": validated_data.volume,
                "open_time": validated_data.open_time.isoformat(),
                "close_time": validated_data.close_time.isoformat(),
                "is_closed": validated_data.is_closed
            }
            
            logger.info(f"OHLCV validé et mis à jour - Symbol: {validated_data.symbol}, Close: {validated_data.close_price}")
            
        except ValidationError as ve:
            logger.error(f"Erreur validation OHLCV (Pydantic): {ve}")
        except Exception as e:
            logger.error(f"Erreur traitement OHLCV: {e}")
        
    async def _process_indicator(self, payload: dict):
            try:
                if not payload:
                    logger.warning("Payload INDICATOR vide")
                    return None
                
                validated_data = IndicatorValidator(**payload)
                self.state["indicators"]={
                    "symbol": validated_data.symbol,
                    "timestamp": validated_data.timestamp,
                    "ema_20": validated_data.ema_20,
                    "ema_50": validated_data.ema_50,
                    "ema_200": validated_data.ema_200,
                    "rsi_14": validated_data.rsi_14,
                    "atr_14": validated_data.atr_14,
                    "macd_line": validated_data.macd_line,
                    "macd_signal": validated_data.macd_signal,
                    "macd_hist": validated_data.macd_hist
                }
            except ValidationError as ve:
                logger.error(f"Erreur validation INDICATOR (Pydantic): {ve}")
            except Exception as e:
                logger.error(f"Erreur traitement INDICATOR: {e}")

    async def _process_sentiment(self, payload: dict):
        try:
            if not payload:
                logger.warning("Payload SENTIMENT vide")
                return None

            validated_data = SentimentValidator(**payload)
            self.state["sentiment"] = {
                "symbol": validated_data.symbol,
                "timestamp": validated_data.timestamp,
                "sentiment_score": validated_data.sentiment_score,
                "sentiment_label": validated_data.sentiment_label,
                "source": validated_data.source
            }

            logger.info(f"Sentiment validé et mis à jour - Symbol: {validated_data.symbol}, Score: {validated_data.sentiment_score}")

        except ValidationError as ve:
            logger.error(f"Erreur validation SENTIMENT (Pydantic): {ve}")
        except Exception as e:
            logger.error(f"Erreur traitement SENTIMENT: {e}")

    async def _process_ml_pred(self, payload: dict):
        pass

    async def _process_account(self, payload: dict):
        try:
            if not payload:
                logger.warning("Payload ACCOUNT vide")
                return None
            # Implémenter après
        except Exception as e:
            logger.error(f"Erreur traitement ACCOUNT: {e}")

    def aggregate_functions(self):
        try:
            context ={
                "timestamp": datetime.now().isoformat(),
                "symbol": self.state.get("OHLCV", {}).get("symbol"),
                "market": {
                    "open": self.state.get("OHLCV", {}).get("open"),
                    "high": self.state.get("OHLCV", {}).get("high"),
                    "low": self.state.get("OHLCV", {}).get("low"),
                    "close": self.state.get("OHLCV", {}).get("close"),
                    "volume": self.state.get("OHLCV", {}).get("volume"),
                    "open_time": self.state.get("OHLCV", {}).get("open_time"),
                    "close_time": self.state.get("OHLCV", {}).get("close_time"),
                    "is_closed": self.state.get("OHLCV", {}).get("is_closed", False)
                },
                "technical": self.state["indicators"] or {},
                "sentiment": self.state["sentiment"] or {},
                "ml_prediction": self.state["ml_prediction"] or {},
                "account": self.state["account"] or {}

            }
            logger.info(f"Contexte agrégé: {context['symbol']}")
            return context
            
        except Exception as e:
            logger.error(f"Erreur agrégation: {e}")
            return None

