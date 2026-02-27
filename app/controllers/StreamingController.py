
from app.services.streaming.QueueManager import QueueManager
from app.pipeline.collectors.MarketDataCollector import MarketDataCollector
from app.stream_processor.StreamProcessor import StreamProcessor 
from app.services.streaming.BinanceStream import BinanceStream
from app.models.enums.KlineIntervalEnum import KlineIntervalEnum
from app.models.enums.symbolEnum import symbolEnum
from app.core.config import Settings
from app.core.Logger import Logger
import asyncio


logger = Logger()

class StreamingController:
    def __init__(self):
        self.processors = {}
        self.settings = Settings()
        self.socket_url = None
        self.queue_manager = None


    async def _get_queue_manager(self):
        if not self.queue_manager:
            self.queue_manager = QueueManager(settings=self.settings)
            await self.queue_manager.connect()
            await self.queue_manager.setup_broker()
            logger.info("QueueManager connected to RabbitMQ.")
        return self.queue_manager


    async def start_stream(self, symbol: str = None, interval: str = None):
        if not symbol:
            symbol = symbolEnum.BTCUSDT.value
        if not interval:
            interval = KlineIntervalEnum.MIN_1.value

        symbol = symbol.lower()

        if symbol in self.processors:
            return {"error": "Stream already started for this symbol"}

        qm = await self._get_queue_manager()

        #await self.queue_manager.connect()
        #await self.queue_manager.setup_broker()
        #logger.info("QueueManager connected to RabbitMQ.")         

        self.socket_url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
        binance_stream = BinanceStream(self.socket_url)
        market_data_collector = MarketDataCollector(binance_stream, qm, "binance")
        
        processor = StreamProcessor(symbol,binance_stream, market_data_collector)
        await processor.initialisation()
        logger.info("StreamProcessor initialized.")

        asyncio.create_task(processor.start())


        self.processors[symbol] = processor
        #example de self.processors =   {"btcusdt": <Objet StreamProcessor (Actif, Connecté à Binance, Connecté à RabbitMQ)>,
        #"ethusdt": <Objet StreamProcessor (Actif, Connecté à Binance, Connecté à RabbitMQ)>}
        return {"status": "started", "symbol": symbol}
        
    
    async def stop_stream(self, symbol: str):
        if not symbol:
            symbol = symbolEnum.BTCUSDT.value

        symbol = symbol.lower()        

        if symbol not in self.processors:
            return {"error": "Stream not found"}
            
        processor = self.processors[symbol]
        
        await processor.stop()
        
        del self.processors[symbol]
        
        return {"status": "stopped", "symbol": symbol}
    async def get_stream_status(self, symbol: str = None):
        if not symbol:
            symbol = symbolEnum.BTCUSDT.value
            
        symbol = symbol.lower()
        
        if symbol in self.processors:
            return await self.processors[symbol].status()
        else:
            return {
                "symbol": symbol,
                "is_running": False,
                "buffer_size": 0,
                "status": "stopped"
            }

# streaming_controller = StreamingController()