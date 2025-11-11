

class MarketData():
    def __init__(self, timestamp,symbol,  Open, High, Low, Close, Volume):
        self.timestamp = timestamp
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume