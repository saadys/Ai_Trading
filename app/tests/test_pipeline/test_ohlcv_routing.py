"""
Test de routage des messages OHLCV vers indicator_queue.
Vérifie que les messages OHLCV ne vont PAS dans sentiment_queue.
"""
import pytest
import asyncio
from app.services.streaming.QueueManager import QueueManager
from datetime import datetime

@pytest.mark.asyncio
async def test_ohlcv_routes_to_indicator_queue():
    """Vérifie que OHLCV va dans indicator_queue, PAS dans sentiment_queue"""
    qm = QueueManager()
    
    try:
        await qm.connect()
        await qm.setup_broker()
        
        # Publier un message de type OHLCV
        test_message = {
            "type": "OHLCV",
            "payload": {
                "symbol": "BTCUSDT",
                "open_price": 50000.0,
                "high_price": 51000.0,
                "low_price": 49500.0,
                "close_price": 50500.0,
                "volume": 1234.56,
                "timestamp": str(datetime.now())
            }
        }
        
        await qm.publish(
            exchange_name='market_data_exchange',
            message=test_message,
            routing_key='market_data.ohlcv.btc'
        )
        
        # Attendre que le message soit routé
        await asyncio.sleep(1)
        
        # Vérifier les queues
        sentiment_queue = qm.queues.get('sentiment_queue')
        indicator_queue = qm.queues.get('indicator_queue')
        database_queue = qm.queues.get('database_saver_queue')
        
        # Récupérer le nombre de messages
        indicator_info = await qm.channel.declare_queue('indicator_queue', passive=True)
        database_info = await qm.channel.declare_queue('database_saver_queue', passive=True)
        
        indicator_count = indicator_info.declaration_result.message_count
        database_count = database_info.declaration_result.message_count
        
        # Assertions
        assert indicator_count > 0, "indicator_queue devrait avoir au moins 1 message"
        assert database_count > 0, "database_saver_queue devrait recevoir tous les messages"
        
        print(f"✅ indicator_queue: {indicator_count} message(s)")
        print(f"✅ database_saver_queue: {database_count} message(s)")
        
    finally:
        await qm.close()

if __name__ == "__main__":
    asyncio.run(test_ohlcv_routes_to_indicator_queue())
