from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
ENV_FILE_ROOT = os.path.join(ROOT_DIR, ".env")
ENV_FILE_APP = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):

    NAME_APP : str = "Ai_Trading"
    APP_VERSION: str = "0.1.0"

############################## Config DB ##############################

    #Postgres_Port : int = 5432
    #Postgres_DBName : str = "postgres" #"Ai_Trading"
    #Postgres_Host : str = "localhost"
    #Postgres_User : str = "postgres"
    #Postgres_Password : str = "saadys"
    Postgres_Port : int = 5432
    Postgres_DBName : str = "ai_trading"
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
    NewsApi_Key: str = "pub_2a69ac0529274d0e9c92983cf2ffdbfd" 
    Model_Sentiment_Name : str = "yiyanghkust/finbert-tone"
    MINIMAX_25_API_KEY : str = ""

    FINBERT_LABELS : list = ['Neutral','Positive', 'Negative']
    model_config = SettingsConfigDict(env_file=(ENV_FILE_ROOT, ENV_FILE_APP), extra="ignore")


############################## Config RabbitMQ ##############################
    RABBITMQ_DEFAULT_VHOST : str = "/"
    #RABBITMQ_DEFAULT_VHOST : str = "localhost"
    RABBITMQ_DEFAULT_USER: str = "myadmin"
    RABBITMQ_DEFAULT_PASS:str = "mypassword"
    #RABBITMQ_DEFAULT_PORTS: int = 5672

    
############################## Config LLMS ##############################



def get_settings():
    return Settings()