import sys
import os
import asyncio
# Ajoute le répertoire 'app' au chemin de recherche de Python
# Se déplace de 'app/tests/test_pipeline' vers 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from services.streaming.QueueManager import QueueManager

async def test_publish():
    qm = QueueManager()
    await qm.connect()
    await qm.setup_broker()

    message = {
        "symbol": "EUR/USD",
        "price": 1.0876
    }

    await qm.publish(
        exchange_name="market_data_exchange",
        routing_key="market_data.eurusd",
        message=message
    )

    print("✔ Message publié !")

asyncio.run(test_publish())