import sys
import os
import asyncio
# Ajoute le répertoire 'app' au chemin de recherche de Python
# Se déplace de 'app/tests/test_pipeline' vers 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Vos imports existants viennent après
from services.streaming.QueueManager import QueueManager

async def main():
    qm = QueueManager()
    await qm.connect()
    await qm.setup_broker()
    print("Connexion + configuration OK")

asyncio.run(main())