from datetime import datetime


class MarketData:
    def __init__(self, open_time:datetime, symbol:str, open_price:float, high_price:float, low_price:float, close_price:float, volume:float, is_closed:bool = False, close_time:datetime = None, exchange_name:str = None):
        self.open_time = open_time
        self.symbol = symbol
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume 
        self.is_closed = is_closed
        self.close_time = close_time
        self.exchange_name = exchange_name
    
    def to_dict(self)-> dict:
        return {
            "open_time": self.open_time,
            "symbol": self.symbol,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "volume": self.volume,
            "is_closed": self.is_closed,
            "close_time": self.close_time,
            "exchange_name": self.exchange_name

        }