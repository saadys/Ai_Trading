from pydantic_settings import BaseSettings

class Setting(BaseSettings):

    NAME_APP : str = "Ai_Trading"
    APP_VERSION: str = "0.1.0"

    Postgres_Host : int 