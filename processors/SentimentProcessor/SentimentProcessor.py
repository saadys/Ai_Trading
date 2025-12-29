import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


from app.services.streaming.QueueManager import QueueManager
from app.models.TableModel import TableModel
from SentimentInterface import SentimentInterface
from app.core.Logger import Logger, logger


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
                logger.info("Traitement du message Data_News")

                title = payload.get("title", "Sans titre")
                Contenu=payload.get("content", "Sans contenu")

                Logger.info(f"Analyse du sentiment pour : {title[:50]}...")
                score,label = await self.strategy.analyse_News(Contenu)

                Logger.info(f"Sentiment : {label} ({score:.2f})")

                envellope = {
                    "type": "Sentiment",
                    "payload": {
                        "title": title,
                        "content": Contenu,
                        "score": score,
                        "label": label
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
        

        