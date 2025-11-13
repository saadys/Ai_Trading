from datetime import datetime


class MarketData:
    def __init__(self, timestamp:datetime, symbol:str, Open:float, High:float, Low:float, Close:float, Volume:int):
        self.timestamp = timestamp
        self.symbol = symbol
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume
    
    def to_dict(self)-> dict:
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "Open": self.Open,
            "High": self.High,
            "Low": self.Low,
            "Close": self.Close,
            "Volume": self.Volume
        }