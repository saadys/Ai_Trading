from app.models.enums.SymbolEnum import SymbolEnum
from app.core.Logger import Logger
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

logger = Logger

class StreamProcessor:
    def __init__(self, symbol, binancestream, market_data_collector):
        self.binancestream = binancestream
        self.market_data_collector = market_data_collector
        self.symbol = symbol
        self.is_running = False
        self.internal_buffer = asyncio.Queue()

    async def initialisation(self):
        if self.symbol not in [s.value for s in SymbolEnum]:
            raise ValueError(f"Invalid symbol: {self.symbol}")
        
        logger.info(f"Initialization complete for {self.symbol}.")

        try:
            q_manager = self.market_data_collector.queue
            await q_manager.connect()
            await q_manager.setup_broker()

            logger.info("Queue manager connected and broker setup completed.")

        except Exception as e:
            logger.error(f"Error during initialization QueueManager: {e}")

        self.binancestream.on_message_callback = self._buffer_message

        logger.info("Initialization complete. System ready.")
            
    async def _buffer_message(self, message: str):
        """Reçoit le message de Binance et le met dans le buffer."""
        await self.internal_buffer.put(message)

    async def start(self):
        self.is_running = True
        logger.info(f"Starting stream processor for {self.symbol}")
        
        asyncio.create_task(self.binancestream.connect_to_binance_stream())
        
        while self.is_running:
            try:
                raw_message = await self.internal_buffer.get()
                
                await self.market_data_collector._process_raw_message(raw_message)
                
                self.internal_buffer.task_done()
                
            except Exception as e:
                logger.error(f"An error occurred in processing loop: {e}")
                await asyncio.sleep(1) 

    async def stop(self):
        try:
            logger.info(f"Stopping StreamProcessor for {self.symbol}...")
            
            self.is_running = False
            
            self.binancestream.on_message_callback = None
            await self.binancestream.disconnect()
            
            # 3. DRAINAGE : Attendre que le buffer soit vide
            if not self.internal_buffer.empty():
                logger.info(f"Draining buffer... {self.internal_buffer.qsize()} messages remaining.")
                # On attend que tous les items mis dans la queue soient marqués 'task_done'
                await self.internal_buffer.join()
            
            logger.info(f"StreamProcessor for {self.symbol} stopped successfully.")
            
        except Exception as e:
            logger.error(f"Error stopping stream for {self.symbol}: {e}")

    async def status(self) -> dict:
        return {
            "symbol": self.symbol,
            "is_running": self.is_running,
            "buffer_size": self.internal_buffer.qsize()
        }