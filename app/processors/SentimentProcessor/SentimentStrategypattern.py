
from app.processors.SentimentProcessor.SentimentInterface import SentimentInterface
from app.core.config import get_settings
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import torch

class SentimentStrategyFinbert(SentimentInterface):
    def __init__(self):
        super().__init__()
        
        self.model_name = get_settings().Model_Sentiment_Name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

        self.FINBERT_LABELS = get_settings().FINBERT_LABELS
        self.device= torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
     
    async def analyse_News(self,text):
        if not text or not text.strip():
            return 0.0, 'Neutral'
    
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True).to(self.device)
    
        with torch.no_grad():
            outputs = self.model(**inputs)
    
        probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
        max_index = np.argmax(probabilities)
    
        return float(probabilities[max_index]), self.FINBERT_LABELS[max_index]   


class SentimentStrategyNLP(SentimentInterface):
    def __init__(self):
        super().__init__()
    
    async def analyse_News(self,text):
        pass 


class SentimentStrategyLLM(SentimentInterface):
    def __init__(self):
        super().__init__()
    
    async def analyse_News(self,text):
        pass 

