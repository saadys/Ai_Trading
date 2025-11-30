import sys
import os
import asyncio
# Ajoute le répertoire 'app' au chemin de recherche de Python
# Se déplace de 'app/tests/test_pipeline' vers 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from services.streaming.QueueManager import QueueManager
import random

async def simulate_market_data():
    qm = QueueManager()
    await qm.connect()
    await qm.setup_broker()

    symbols = ["BTCUSDT", "ETHUSDT", "EURUSD"]

    while True:
        symbol = random.choice(symbols)
        price = round(random.uniform(1000, 60000), 2)

        await qm.publish(
            "market_data_exchange",
            {"symbol": symbol, "price": price},
            routing_key=f"market_data.{symbol.lower()}"
        )

        print(f"📤 envoyé : {symbol} → {price}")
        await asyncio.sleep(1)

asyncio.run(simulate_market_data())