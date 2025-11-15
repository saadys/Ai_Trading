from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    NAME_APP : str = "Ai_Trading"
    APP_VERSION: str = "0.1.0"

    Postgres_Port : int = 5432
    Postgres_DBName : str = "Ai_Trading"
    Postgres_Host : str = "localhost"
    Postgres_User : str = "postgres"
    Postgres_Password : str = "minirag222"

    DEEPSEEK_API_KEY : str = "sk-334b053280444fc08bd37699116a7244"
    OPENAI_API_KEY : str = "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"
    QWEN_kEY : str = "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"
    BINANCE_API_KEY : str = ""

    RABBITMQ_DEFAULT_VHOST : str = "localhost"
    RABBITMQ_DEFAULT_USER: str = "myadmin"
    RABBITMQ_DEFAULT_PASS:str = "mypassword"
    #RABBITMQ_DEFAULT_PORTS: int = 5672

def get_settings():
    return Settings()