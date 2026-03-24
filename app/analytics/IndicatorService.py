from app.core.logger import Logger, logger
from app.services.streaming.QueueManager import QueueManager
from app.models.enums.SymbolEnum import SymbolEnum
from app.services.streaming.IndicatorValidator import IndicatorValidator
from pydantic import ValidationError
from collections import deque
import numpy as np
import talib
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

logger = Logger()

class IndicatorService:
    def __init__(self, queue_manager: QueueManager, symbol: SymbolEnum):
        self.queue = queue_manager
        self.symbol = symbol.value
        self.prices_buffer = deque(maxlen=250)
        self.highs_buffer = deque(maxlen=250)
        self.lows_buffer = deque(maxlen=250)
    
    async def calculate_indicators(self):
        if not self.queue.connection or self.queue.connection.is_closed:
            logger.info("Connecting to RabbitMQ")
            await self.queue.connect()

        logger.info("Setting up broker")
        await self.queue.setup_broker()

        await self.queue.consume(
            queue_name='indicator_queue',
            on_message_callback=self.process_message
        )

    async def process_message(self, message: dict):
        payload_message = message.get('payload') if isinstance(message, dict) else None
        if not isinstance(payload_message, dict):
            payload_message = message if isinstance(message, dict) else {}

        # BUGFIX: Compare symbols case-insensitively (Binance sends BTCUSDT, enum stores btcusdt)
        if payload_message.get('symbol', '').upper() != self.symbol.upper():
            return False

        try:
            raw_close = payload_message.get('close_price')
            raw_high = payload_message.get('high_price')
            raw_low = payload_message.get('low_price')

            if raw_close is None:
                return False

            close_price = float(raw_close)
            high_price = float(raw_high) if raw_high else close_price
            low_price = float(raw_low) if raw_low else close_price
            
            self.prices_buffer.append(close_price)
            self.highs_buffer.append(high_price)
            self.lows_buffer.append(low_price)
            
            # Dictionnaire pour collecter les indicateurs calculés
            indicators_data = {
                "symbol": self.symbol,
                "timestamp": None # À remplacer par le vrai timestamp du message si disponible
            }
            
            # Calculs (seule condition : avoir assez de données)
            if len(self.prices_buffer) >= 20:
                np_closes = np.array(self.prices_buffer)
                np_highs = np.array(self.highs_buffer)
                np_lows = np.array(self.lows_buffer)
                
                #  EMA 20 
                ema_20 = talib.EMA(np_closes, timeperiod=20)[-1]
                indicators_data["ema_20"] = float(ema_20)
                logger.info(f"[{self.symbol}] EMA 20: {ema_20:.2f}")

                #  EMA 50 
                if len(self.prices_buffer) >= 50:
                    ema_50 = talib.EMA(np_closes, timeperiod=50)[-1]
                    indicators_data["ema_50"] = float(ema_50)
                    logger.info(f"[{self.symbol}] EMA 50: {ema_50:.2f}")

                #  EMA 200 
                if len(self.prices_buffer) >= 200:
                    ema_200 = talib.EMA(np_closes, timeperiod=200)[-1]
                    indicators_data["ema_200"] = float(ema_200)
                    logger.info(f"[{self.symbol}] EMA 200: {ema_200:.2f}")

                #  RSI 14 
                if len(self.prices_buffer) >= 14:
                    rsi = talib.RSI(np_closes, timeperiod=14)[-1]
                    indicators_data["rsi_14"] = float(rsi)
                    logger.info(f"[{self.symbol}] RSI 14: {rsi:.2f}")

                #  ATR 14 (Volatilité) 
                if len(self.prices_buffer) >= 14:
                    atr = talib.ATR(np_highs, np_lows, np_closes, timeperiod=14)[-1]
                    indicators_data["atr_14"] = float(atr)
                    logger.info(f"[{self.symbol}] ATR 14: {atr:.2f}")

                #  MACD 
                if len(self.prices_buffer) >= 26:
                    macd, macd_signal, macd_hist = talib.MACD(
                        np_closes, 
                        fastperiod=12, 
                        slowperiod=26, 
                        signalperiod=9
                    )
                    indicators_data["macd_line"] = float(macd[-1])
                    indicators_data["macd_signal"] = float(macd_signal[-1])
                    indicators_data["macd_hist"] = float(macd_hist[-1])
                    logger.info(f"[{self.symbol}] MACD: {macd[-1]:.2f} | Signal: {macd_signal[-1]:.2f} | Hist: {macd_hist[-1]:.2f}")
                
                try:
                    validated_data = IndicatorValidator(**indicators_data)
                    
                    envolloppe = {
                        "type" : "INDICATOR",
                        "payload" : validated_data.dict()
                    }
                    await self.queue.publish(
                        exchange_name='market_data_exchange', 
                        message=envolloppe, 
                        routing_key='market_data.indicators.btc' 
                    )                    
                except ValidationError as e:
                    logger.error(f"Error validating indicators: {e}")
                
        except ValueError as e:
            logger.error(f"error converting prices: {e}")
        except Exception as e:
            logger.error(f"Error in IndicatorService.process_message: {e}")
