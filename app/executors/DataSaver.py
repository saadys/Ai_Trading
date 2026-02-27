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
        self.batch_size = batch_size

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

            elif message.get("type") == "DATA_NEWS":
                self.data_news_batch.append(message["payload"])
                
                if len(self.data_news_batch) >= self.batch_size:
                    logger.info(f"Batch DATA_NEWS full ({self.batch_size} items). Saving to DB...")
                    try:
                        await self.table_model.save_data_news_batch(self.data_news_batch)
                        logger.info("DATA_NEWS Batch saved successfully.")
                    except Exception as db_e:
                        logger.error(f"Database error while saving DATA_NEWS: {db_e}", exc_info=True)
                    finally:
                        self.data_news_batch = []
        except Exception as e:
            logger.error(f"Error parsing or processing message in DataSaver: {e}", exc_info=True)