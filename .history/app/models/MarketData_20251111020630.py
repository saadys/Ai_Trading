from datetime import datetime


class MarketData:
    def __init__(self, timestamp:datetime, symbol:str, Open:, High, Low, Close, Volume):
        self.timestamp = timestamp
        self.symbol = symbol
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume
    
    def to_dict(self)-> dict