import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.models.db_schemas.mini_Trading.schemas.MarketData import MarketData
from app.services.streaming.QueueManager import QueueManager
from app.models.TableModel import TableModel
from app.core.logger import Logger, logger

logger = Logger()

class DataSaver:
    def __init__(self, queuemanager: QueueManager, database_manager, batch_size: int = 100):
        
        self.queue = queuemanager
        self.table_model = TableModel(database_manager) 
        self.ohlcv_batch = []
        self.indicator_batch = []
        self.data_news_batch = []
        self.ml_prediction_batch = []
        self.batch_size = batch_size
        
        # Stats observabilité
        self.ml_prediction_processed = 0
        self.ml_prediction_saved = 0
        self.ml_prediction_errors = 0

    async def start(self):
        if not self.queue.connection or self.queue.connection.is_closed:
            logger.info("Connecting to RabbitMQ")
            await self.queue.connect()

        logger.info("Setting up broker")
        await self.queue.setup_broker()

        await self.queue.consume(
            queue_name='database_saver_queue',
            on_message_callback=self.process_message
        )
        logger.info("DataSaver started and listening.")   
           
    async def process_message(self, message: dict):
        try:
            if message.get("type") == "OHLCV":
                self.ohlcv_batch.append(message["payload"])
                
                if len(self.ohlcv_batch) >= self.batch_size:
                    logger.info(f"Batch OHLCV full ({self.batch_size} items). Saving to DB...")
                    try:
                        await self.table_model.save_ohlcv_batch(self.ohlcv_batch)
                        logger.info("OHLCV Batch saved successfully.")
                    except Exception as db_e:
                        logger.error(f"Database error while saving OHLCV: {db_e}", exc_info=True)
                    finally:
                        self.ohlcv_batch = [] 
            
            elif message.get("type") == "INDICATOR":
                self.indicator_batch.append(message["payload"])
                
                if len(self.indicator_batch) >= self.batch_size:
                    logger.info(f"Batch INDICATOR full ({self.batch_size} items). Saving to DB...")
                    try:
                        await self.table_model.save_indicator_batch(self.indicator_batch)
                        logger.info("INDICATOR Batch saved successfully.")
                    except Exception as db_e:
                        logger.error(f"Database error while saving INDICATOR: {db_e}", exc_info=True)
                    finally:
                        self.indicator_batch = []

            elif message.get("type") in ("Data_News", "DATA_NEWS"):
                self.data_news_batch.append(message["payload"])
                
                if len(self.data_news_batch) >= self.batch_size:
                    logger.info(f"Batch Data_News full ({self.batch_size} items). Saving to DB...")
                    try:
                        await self.table_model.save_data_news_batch(self.data_news_batch)
                        logger.info("Data_News Batch saved successfully.")
                    except Exception as db_e:
                        logger.error(f"Database error while saving Data_News: {db_e}", exc_info=True)
                    finally:
                        self.data_news_batch = []
                        
            elif message.get("type") == "ml_prediction":
                self.ml_prediction_processed += 1
                
                event_id = message.get("event_id", "unknown")
                event_version = message.get("event_version", 1)
                payload = message.get("payload", {})
                
                if not payload or payload.get("prediction") is None:
                    logger.warning(f"[LSTM] Payload invalide (event_id={event_id}). Ignoré.")
                    self.ml_prediction_errors += 1
                    return
                
                logger.info(
                    f"\n{'='*50}\n"
                    f" [DataSaver] Sauvegarde LSTM Prédiction \n"
                    f"Event ID    : {event_id}\n"
                    f"Symbol      : {payload.get('symbol', 'N/A')}\n"
                    f"Prediction  : {payload.get('prediction')}\n"
                    f"Probabilité : {payload.get('probability', 'N/A')}\n"
                    f"{'='*50}\n"
                )
                
                self.ml_prediction_batch.append({
                    **payload,
                    "event_id": event_id,
                    "event_version": event_version
                })
                
                if len(self.ml_prediction_batch) >= 1:
                    logger.info("Sauvegarde LSTM immédiate (réactivité prioritaire)...")
                    try:
                        await self.table_model.save_ml_prediction_batch(self.ml_prediction_batch)
                        self.ml_prediction_saved += 1
                        logger.info(f" Prédiction sauvegardée (event_id={event_id})")
                    except Exception as db_e:
                        # Classification erreur pour observabilité
                        error_str = str(db_e).lower()
                        if any(term in error_str for term in ["connection", "timeout", "deadlock"]):
                            logger.warning(
                                f" Erreur temporaire DB (event_id={event_id}, retry). "
                                f"Détail: {db_e}"
                            )
                        else:
                            logger.error(
                                f"Erreur permanente DB (event_id={event_id}, DLQ). "
                                f"Détail: {db_e}"
                            )
                        self.ml_prediction_errors += 1
                    finally:
                        self.ml_prediction_batch = []
                        
        except Exception as e:
            logger.error(f"Error parsing or processing message in DataSaver: {e}", exc_info=True)