import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.services.streaming.QueueManager import QueueManager
from app.models.pydantic.NewsCollectorValidator import NewsCollectorValidator
from pydantic import ValidationError
from datetime import datetime
import asyncio
from newsdataapi import NewsDataApiClient
from app.core.logger import Logger, logger

logger = Logger()

class NewsCollector:
    def __init__(self, queuemanager: QueueManager, exchange_name: str, api_key: str = None):
        self.queuemanager = queuemanager
        self.exchange_name = exchange_name
        self.api = NewsDataApiClient(apikey=api_key)

    async def start_collection_loop(self):
        while True:
            try:
                raw_articles = await self.fetch_crypto_news()
                
                for raw in raw_articles:
                    try:
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
                        envolloppe = {
                            "type" : "Data_News",
                            "payload" : article.to_dict()
                        }
                        
                        if self.queuemanager:
                            await self.queuemanager.publish(
                                exchange_name=self.exchange_name,
                                message=envolloppe,
                                routing_key='market_data.news.btc'
                            )
                            logger.info(f"Published article: {article.title[:30]}...")
                            
                    except ValidationError as e:
                        logger.error(f"Validation failed for article: {e}")
                
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
            
            logger.info("Sleeping for 15 minutes...")
            await asyncio.sleep(900) 

    async def fetch_crypto_news(self):
        articles = []
        try:
            response = await asyncio.to_thread(self.api.crypto_api, q='binance square', language='en')
            
            if response and 'results' in response:
                articles = response['results']
                print(f" {len(articles)} articles")
            else:
                print(" No articles found or error in response.")
                logger.warning(f"Response content: {response}")

        except Exception as e:
            logger.error(f"Erreur NewsData API: {e}")
            
        return articles

