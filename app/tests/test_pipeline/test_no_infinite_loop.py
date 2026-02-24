"""
Test pour vérifier l'absence de boucle infinie dans sentiment_queue.
Vérifie que les messages Sentiment ne reviennent PAS dans sentiment_queue.
"""
import pytest
import asyncio
from app.services.streaming.QueueManager import QueueManager
from datetime import datetime

@pytest.mark.asyncio
async def test_sentiment_output_not_looped_back():
    """Vérifie que les messages Sentiment ne reviennent PAS dans sentiment_queue"""
    qm = QueueManager()
    
    try:
        await qm.connect()
        await qm.setup_broker()
        
        # Purger la queue avant le test
        sentiment_queue = qm.queues.get('sentiment_queue')
        await sentiment_queue.purge()
        
        # Compter les messages initiaux
        initial_info = await qm.channel.declare_queue('sentiment_queue', passive=True)
        initial_count = initial_info.declaration_result.message_count
        
        # Publier un message de type Sentiment (sortie de SentimentProcessor)
        test_message = {
            "type": "Sentiment",
            "payload": {
                "title": "Test article",
                "content": "Test content",
                "score": 0.85,
                "label": "Positive",
                "timestamp": str(datetime.now())
            }
        }
        
        await qm.publish(
            exchange_name='market_data_exchange',
            message=test_message,
            routing_key='market_data.sentiment.btc'
        )
        
        # Attendre que le message soit routé
        await asyncio.sleep(1)
        
        # Vérifier que sentiment_queue n'a PAS reçu le message
        final_info = await qm.channel.declare_queue('sentiment_queue', passive=True)
        final_count = final_info.declaration_result.message_count
        
        # Vérifier database_saver_queue (devrait recevoir le message)
        database_info = await qm.channel.declare_queue('database_saver_queue', passive=True)
        database_count = database_info.declaration_result.message_count
        
        # Assertions
        assert final_count == initial_count, \
            f"sentiment_queue ne devrait PAS recevoir de messages Sentiment (avant: {initial_count}, après: {final_count})"
        
        assert database_count > 0, \
            "database_saver_queue devrait recevoir tous les messages (y compris Sentiment)"
        
        print(f"✅ Pas de boucle infinie: sentiment_queue n'a pas reçu le message Sentiment")
        print(f"✅ database_saver_queue: {database_count} message(s)")
        
    finally:
        await qm.close()

if __name__ == "__main__":
    asyncio.run(test_sentiment_output_not_looped_back())
