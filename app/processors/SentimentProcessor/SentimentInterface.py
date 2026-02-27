from abc import ABC , abstractmethod

class SentimentInterface(ABC):
    @abstractmethod
    def analyse_News(self,text):
        pass 