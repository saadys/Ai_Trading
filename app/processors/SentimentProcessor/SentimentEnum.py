from enum import Enum

class SentimentStrategy(Enum):
    FINBERT = "finbert"
    CLASSICAL_NLP = "classical_nlp"
    LLM = "llm"