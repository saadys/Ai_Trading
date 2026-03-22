import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


from app.services.streaming.QueueManager import QueueManager
from app.models.TableModel import TableModel
from app.processors.SentimentProcessor.SentimentInterface import SentimentInterface
from app.core.logger import Logger, logger
from datetime import datetime


logger = Logger()

class SentimentProcessor():
    def __init__(self,queuemanager: QueueManager,strategy : SentimentInterface,database_manager, batch_size: int = 100):
        self.queuemanager = queuemanager
        self.strategy = strategy
        self.database_manager = database_manager
        self.batch_size = batch_size

    async def start(self):
        if not self.queuemanager.connection or self.queuemanager.connection.is_closed:
            Logger.info("Connecting to RabbitMQ")
            await self.queuemanager.connect()

        Logger.info("Setting up broker")
        await self.queuemanager.setup_broker()

        await self.queuemanager.consume(
            queue_name='sentiment_queue',
            on_message_callback=self.process_message
        )
        Logger.info("SentimentProcessor started and listening.")   

    async def process_message(self, message: dict):
        try:
            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "Data_News":
                title = ((payload or {}).get("title") or "")
                contenu = ((payload or {}).get("content") or "")

                logger.info(
                    f"\n{'='*40}\n"
                    f" NOUVELLE NEWS DÉTECTÉE \n"
                    f"Titre : {title[:50] if title else 'N/A'}...\n"
                    f"Source: {payload.get('source', 'News')}\n"
                    f"{'='*40}\n"
                )

                score,label = await self.strategy.analyse_News(contenu)

                Logger.info(
                    f"\n{'='*40}\n"
                    f" ANALYSE SENTIMENT (FinBERT) \n"
                    f"Sentiment   : {label}\n"
                    f"Probabilité : {score:.2f}\n"
                    f"{'='*40}\n"
                )

                envellope = {
                    "type": "Sentiment",
                    "payload": {
                        "symbol": payload.get("symbol", "BTCUSDT"),
                        "timestamp": datetime.now().isoformat(),
                        "title": title,
                        "content": contenu,
                        "sentiment_score": score,
                        "sentiment_label": label,
                        "source": payload.get("source", "News")
                    }
                }

                await self.queuemanager.publish(
                    exchange_name='market_data_exchange',
                    message=envellope,
                    routing_key='market_data.sentiment.btc'
                )
                
                
        except Exception as e:
            Logger.error(f"Erreur lors du traitement du message dans SentimentProcessor: {e}")

    #async def analyse_News(self,text):
    #    if not text or not text.strip():
    #        return 0.0, 'Neutral'
    #
    #    inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True).to(self.device)
    #
    #    with torch.no_grad():
    #        outputs = self.model(**inputs)
    #
    #    probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
    #    max_index = np.argmax(probabilities)
    #
    #    return float(probabilities[max_index]), self.FINBERT_LABELS[max_index]
        

        