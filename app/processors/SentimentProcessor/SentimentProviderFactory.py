
from app.processors.SentimentProcessor.SentimentStrategypattern import SentimentStrategyFinbert, SentimentStrategyNLP, SentimentStrategyLLM
from app.processors.SentimentProcessor.SentimentEnum import SentimentStrategy

class SentimentStrategyFactory:
    @staticmethod
    def get_strategy(strategy_type: str):
        if strategy_type == SentimentStrategy.FINBERT.value :
            return SentimentStrategyFinbert()
        elif strategy_type == SentimentStrategy.CLASSICAL_NLP.value:
            return SentimentStrategyNLP()
        elif strategy_type == SentimentStrategy.LLM.value:
            return SentimentStrategyLLM()
        else:
            raise ValueError(f"Stratégie inconnue: {strategy_type}")