import sys
import os
import asyncio
import logging
import traceback


# 1. Setup Environment & Imports
# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Configure Logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("IntegrationTest")

from app.services.streaming.QueueManager import QueueManager
from app.services.streaming.BinanceStream import BinanceStream
from app.pipeline.collectors.MarketDataCollector import MarketDataCollector
from app.stream_processor.StreamProcessor import StreamProcessor
from app.core.Config import Settings
from app.core.Logger import LoggerConfig

async def run_integration_test():
    logger.info("--- Starting Real Integration Test ---")
    
    # Initialize App Logger (required by StreamProcessor)
    LoggerConfig(db_session=None)

    # 2. Configuration
    # Manually set settings to match docker-compose for local testing
    settings = Settings()
    settings.RABBITMQ_DEFAULT_USER = "myadmin"
    settings.RABBITMQ_DEFAULT_PASS = "mypassword"
    settings.RABBITMQ_DEFAULT_VHOST = "/"
    settings.Postgres_Host = "localhost" # Not used but required by Config
    
    # RabbitMQ Connection URL
    rabbitmq_url = f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@localhost:5672/"
    logger.info(f"RabbitMQ URL: {rabbitmq_url}")

    # Binance URL (Public)
    binance_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
    logger.info(f"Binance URL: {binance_url}")

    # 3. Initialize Components
    try:

        queue_manager = QueueManager(settings=settings)
        await queue_manager.connect()
        await queue_manager.setup_broker()
        logger.info("QueueManager connected to RabbitMQ.")

        # BinanceStream
        binance_stream = BinanceStream(binance_url)
        logger.info("BinanceStream initialized.")

        # MarketDataCollector
        collector = MarketDataCollector(binance_stream, queue_manager, "binance")
        logger.info("MarketDataCollector initialized.")

        # --- INTERCEPTION FOR DEMO ---
        # We intercept the method to show data in the console
        original_process = collector._process_raw_message
        
        async def intercepted_process_message(message: str):
            # Log the received data (truncated to avoid spam)
            logger.info(f"DATA RECEIVED: {message[:150]}...") 
            await original_process(message)
            
        collector._process_raw_message = intercepted_process_message
        # -----------------------------

        # StreamProcessor
        processor = StreamProcessor("btcusdt", binance_stream, collector)
        await processor.initialisation()
        logger.info("StreamProcessor initialized.")

        # 4. Start Processing
        logger.info("Starting StreamProcessor (will run for 10 seconds)...")
        
        # Start the processor in a background task
        processor_task = asyncio.create_task(processor.start())

        # Let it run for 10 seconds
        for i in range(10):
            await asyncio.sleep(1)
            status = await processor.status()
            logger.info(f"Running... Buffer Size: {status['buffer_size']}")

        # 5. Stop
        logger.info("Stopping StreamProcessor...")
        await processor.stop()
        
        # Wait for task to finish
        await processor_task
        logger.info("StreamProcessor stopped.")

    except Exception as e:
        logger.error(f"Test Failed: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("--- Test Finished ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_integration_test())
    except KeyboardInterrupt:
        pass
