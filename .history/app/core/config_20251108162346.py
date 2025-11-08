from pydantic_settings import BaseSettings

class Setting(BaseSettings):

    NAME_APP : str = "Ai_Trading"
    APP_VERSION: str = "0.1.0"

    Postgres_Port : int = "5432" 
    Postgres_DBName : str = "Ai_Trading"
    Postgres_Host : str = "localhost"
    Postgres_User : str = "postgres"
    Postgres_Password : str = "password"



def get_settings():
    return Settings()