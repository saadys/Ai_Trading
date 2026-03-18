from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class SentimentValidator(BaseModel):
    symbol: str = Field(..., description="Symbole concerné (ex: BTC)")
    timestamp: datetime = Field(..., description="Date et heure de l'article/analyse")
    sentiment_score: float = Field(..., ge=0.0, le=1.0, description="Probabilité du sentiment (0 à 1)")
    sentiment_label: str = Field(..., pattern="^(Positive|Negative|Neutral)$", description="Label du sentiment (Strictement Positive, Negative ou Neutral)")
    title: Optional[str] = Field(None, description="Titre de l'article analysé")
    source: Optional[str] = Field(None, description="Source de l'article (ex: Google News)")

    model_config = ConfigDict(populate_by_name=True)