from sqlalchemy import Table, Column, Integer, String
from schemas import SQLAlchemyBase


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Log(SQLAlchemyBase):


    
