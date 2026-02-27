import sys
import os
import asyncio
# Ajoute le répertoire 'app' au chemin de recherche de Python
# Se déplace de 'app/tests/test_pipeline' vers 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from services.streaming.QueueManager import QueueManager

async def on_message(msg):
    print("📩 Message reçu par le callback :", msg)

async def main():
    qm = QueueManager()
    await qm.connect()
    await qm.setup_broker()

    # Démarrer le consommateur
    await qm.consume("indicator_queue", on_message)

    # Publier un message
    await qm.publish(
        "market_data_exchange",
        {"symbol": "BTC/USDT", "price": 55000},
        routing_key="market_data.btcusdt"
    )

    # Laisser le consumer recevoir
    await asyncio.sleep(2)

asyncio.run(main())