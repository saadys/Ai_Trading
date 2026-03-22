from abc import ABC, abstractmethod


class LLMInterface(ABC):
    @abstractmethod
    async def aggregate_responses(self,context:dict):
        """
        Return Decision from All Sources (OHLCV, Indicators, Sentiment, ML Predictions, Account Info)
        """
        pass

    @abstractmethod
    def Text_To_JSON(self,response:str):
        """ 
        Convertit une réponse textuelle en format JSON structuré.
        """
        pass
