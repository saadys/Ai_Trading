from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NewsCollectorValidator(BaseModel):

    article_id: Optional[str] = Field(None, alias="article_id")
    title: str = Field(..., description="Titre de la news")
    link: Optional[str] = Field(None, description="Lien source")
    pub_date: datetime = Field(..., description="Date de publication")
    content: Optional[str] = Field(None, description="Contenu ou description")
    source_id: Optional[str] = Field(None, description="Identifiant source (ex: binance)")
    categories: Optional[List[str]] = Field(default_factory=list, description="Catégories associées")
    
    # Champs ajoutés par notre collecteur
    symbol: str = Field(..., description="Symbole crypto concerné (ex: BTC)")
    timestamp: datetime = Field(..., description="Timestamp normalisé pour notre système")

    class Config:
        populate_by_name = True
