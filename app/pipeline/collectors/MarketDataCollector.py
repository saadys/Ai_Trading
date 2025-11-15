from app.models.MarketData import MarketData
from app.services.streaming.QueueManager import QueueManager
from app.services.streaming.BinanceStream import BinanceStream
from app.core.Logger import Logger, logger

logger = logger()
class MarketDataCollector:
    
    def __init__(self, stream: BinanceStream, queue: QueueManager, exchange_name: str):
        self.stream = stream
        self.queue = queue
        self.exchange_name = exchange_name
        
        self.stream.on_message_callback = self._process_raw_message
        
    async def start_collecting(self):
        logger.info("Démarrage de la collecte des données de marché...")
        await self.stream.connect_to_binance_stream
    
         
    

 