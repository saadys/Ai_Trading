from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):

    NAME_APP : str = "Ai_Trading"
    APP_VERSION: str = "0.1.0"

############################## Config DB ##############################

    #Postgres_Port : int = 5433
    #Postgres_DBName : str = "postgres" #"Ai_Trading"
    #Postgres_Host : str = "localhost"
    #Postgres_User : str = "postgres"
    #Postgres_Password : str = "saadys"
    Postgres_Port : int = 5433
    Postgres_DBName : str = "Ai_Trading"
    Postgres_Host : str = "localhost"
    Postgres_User : str = "postgres"
    Postgres_Password : str = "saadys"

############################## Config LLMS ##############################

    DEEPSEEK_API_KEY : str = ""
    DEEPSEEK_BASE_URL : str = ""
    OPENAI_API_KEY : str = ""
    QWEN_kEY : str = ""
    BINANCE_API_KEY : str = ""
    GEMINI_API_KEY : str = ""

    Model_Sentiment_Name : str = "yiyanghkust/finbert-tone"

    FINBERT_LABELS : list = ['Neutral','Positive', 'Negative']
    model_config = SettingsConfigDict(env_file=ENV_FILE)


############################## Config RabbitMQ ##############################
    RABBITMQ_DEFAULT_VHOST : str = "/"
    #RABBITMQ_DEFAULT_VHOST : str = "localhost"
    RABBITMQ_DEFAULT_USER: str = "myadmin"
    RABBITMQ_DEFAULT_PASS:str = "mypassword"
    #RABBITMQ_DEFAULT_PORTS: int = 5672

    
############################## Config LLMS ##############################



def get_settings():
    return Settings()