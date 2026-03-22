import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


from app.services.streaming.QueueManager import QueueManager
from app.services.streaming.BinanceStream import BinanceStream
from app.services.streaming.DataValidator import DataValidator
from app.models.MarketData import MarketData
from app.core.logger import Logger, logger
from json import JSONDecodeError
from pydantic import ValidationError
from datetime import datetime
import json

logger = logger()

class MarketDataCollector:
    def __init__(self, binancestream: BinanceStream, queuemanager: QueueManager, exchange_name: str):
        self.stream = binancestream
        self.queue = queuemanager
        self.exchange_name = exchange_name
        
        self.stream.on_message_callback = self._process_raw_message


    async def _process_raw_message(self,message:str ):
        try:
            message = json.loads(message)
            kline = message['k']

            if not kline.get('x', False):
                return

            raw_data = {
                'symbol': kline['s'],
                'open_time': datetime.fromtimestamp(kline['t'] / 1000),
                'o': float(kline['o']),
                'h': float(kline['h']),
                'l': float(kline['l']),
                'c': float(kline['c']),
                'v': float(kline['v']),
                'close_time': datetime.fromtimestamp(kline['T'] / 1000),
                'is_closed': kline['x']
            }

            validated_data = DataValidator(**raw_data)
        
            market_data = MarketData(
                    symbol = validated_data.symbol,
                    open_time = validated_data.open_time,
                    open_price = validated_data.open_price,
                    high_price = validated_data.high_price,
                    low_price = validated_data.low_price,
                    close_price = validated_data.close_price,
                    volume = validated_data.volume,
                    close_time=validated_data.close_time,
                    is_closed=validated_data.is_closed,
                    exchange_name=self.exchange_name
            )

            envolloppe = {
                "type" : "OHLCV",
                "payload" : market_data.to_dict()
            }

            await self.queue.publish(
                exchange_name='market_data_exchange',
                message=envolloppe, 
                routing_key='market_data.ohlcv.btc'
            )

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
        except JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
        except KeyError as e:
            logger.error(f"Missing key in data: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement: {e}")

    async def start_collecting(self):
        logger.info("Démarrage de la collecte des données de marché...")
        await self.stream.connect_to_binance_stream()
