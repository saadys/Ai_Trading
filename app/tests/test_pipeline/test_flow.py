import asyncio
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from .services.streaming.BinanceStream import BinanceStream
from .services.streaming.QueueManager import QueueManager
from .pipeline.collectors.MarketDataCollector import MarketDataCollector
from .stream_processor.StreamProcessor import StreamProcessor
from .core.Logger import Logger

# Configurer le logger pour voir les infos dans la console
import logging
logging.basicConfig(level=logging.INFO)

async def main():
    print("--- Démarrage du Test ---")
    
    # 1. Initialiser les composants
    # URL WebSocket Binance pour BTCUSDT (kline 1m)
    socket_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
    
    binance_stream = BinanceStream(socket_url=socket_url)
    queue_manager = QueueManager() # Assurez-vous que les params RabbitMQ sont bons (localhost?)
    
    # Le collecteur qui va transformer le JSON Binance -> Objet MarketData -> RabbitMQ
    collector = MarketDataCollector(
        binancestream=binance_stream, 
        queuemanager=queue_manager, 
        exchange_name="binance"
    )
    
    # Le processeur qui orchestre tout
    processor = StreamProcessor(
        symbol="BTCUSDT", 
        binancestream=binance_stream, 
        market_data_collector=collector
    )
    
    # 2. Initialisation (Connexion RabbitMQ)
    print("1. Initialisation...")
    await processor.initialisation()
    
    # 3. Démarrage du flux
    print("2. Démarrage du Stream (Laissez tourner 10 secondes)...")
    # On lance start() en tâche de fond pour ne pas bloquer
    task = asyncio.create_task(processor.start())
    
    # On attend 10 secondes pour laisser passer quelques messages
    await asyncio.sleep(10)
    
    # 4. Arrêt propre
    print("3. Arrêt du Stream (Test du drainage)...")
    await processor.stop()
    
    # On attend que la tâche se termine vraiment
    try:
        await task
    except asyncio.CancelledError:
        pass
        
    print("--- Test Terminé ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Arrêt manuel.")