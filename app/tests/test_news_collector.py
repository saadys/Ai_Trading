import sys
import os
import asyncio
import websockets

# Adjust path to import from app
# Assumes structure: Ai_Trading/app/tests/test_news_collector.py
# We want to add Ai_Trading to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.pipeline.collectors.NewsCollector import NewsCollector
from app.services.streaming.QueueManager import QueueManager
from app.core.Logger import Logger, LoggerConfig
from app.models.pydantic.NewsCollectorValidator import NewsCollectorValidator
from pydantic import ValidationError
from datetime import datetime

async def test_news_collector():
    # Initialisation du Logger
    LoggerConfig(db_session=None)
    
    Logger.info("--- Démarrage du test NewsCollector ---")
    
    # Pour tester, mettez votre clé ici ou utilisez l'environnement
    # Exemple: set NEWSDATA_API_KEY=votre_cle
    api_key_test = os.environ.get("NEWSDATA_API_KEY", "pub_2a69ac0529274d0e9c92983cf2ffdbfd")
    
    Logger.info(f"Utilisation de la clé API : {api_key_test}")
    
    # On passe None pour le QueueManager car on veut juste tester la récupération
    # et éviter de se connecter à RabbitMQ
    collector = NewsCollector(queuemanager=None, exchange_name="test_exchange", api_key=api_key_test)
    
    Logger.info("Appel de fetch_crypto_news()...")
    articles = await collector.fetch_crypto_news()
    
    Logger.info(f"\n--- Résultat du test ---")
    Logger.info(f"Nombre d'articles reçus : {len(articles)}")
    
    for i, raw in enumerate(articles[:50]):
        Logger.info(f"\nTraitement Article {i+1}:")
        try:
            # Validation via le modèle Pydantic NewsArticle
            article = NewsCollectorValidator(
                article_id=raw.get('article_id'),
                title=raw.get('title'),
                link=raw.get('link'),
                pub_date=raw.get('pubDate'),
                content=raw.get('description') or raw.get('content'),
                source_id=raw.get('source_id'),
                categories=raw.get('category') if isinstance(raw.get('category'), list) else [raw.get('category')] if raw.get('category') else [],
                symbol='BTC',
                timestamp=datetime.now()
            )
            Logger.info(f"  [VALIDE] Titre: {article.title[:50]}...")
            Logger.info(f"  Source: {article.source_id} | Date: {article.pub_date}")
            Logger.info(f"  ID: {article.article_id} | Categories: {article.categories}")
            Logger.info(f"  Lien: {article.link}")
            Logger.info(f"  Contenu: {article.content[:100] if article.content else 'N/A'}...")
            Logger.info(f"  Symbol: {article.symbol} | Collection Time: {article.timestamp}")
        except ValidationError as e:
            Logger.error(f"  [ERREUR VALIDATION] Article {i+1}: {e}")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test_news_collector())
    except KeyboardInterrupt:
        print("\nTest arrêté par l'utilisateur.")
