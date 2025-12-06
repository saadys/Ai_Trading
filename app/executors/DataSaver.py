import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


from app.services.streaming.QueueManager import QueueManager
from app.models.TableModel import TableModel
from app.core.Logger import Logger, logger

logger = Logger()

class DataSaver:
    def __init__(self,queuemanager : QueueManager,database_manager):
        
        self.queue = queuemanager
        self.table_model = TableModel(database_manager) 
        self.ohlcv_batch = []

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
        if message.get("type") == "OHLCV":
            self.ohlcv_batch.append(message["payload"])
            
            if len(self.ohlcv_batch) >= 100:
                logger.info(f"Batch full (100 items). Saving to DB...")
                await self.table_model.save_ohlcv_batch(self.ohlcv_batch)
                self.ohlcv_batch = [] 