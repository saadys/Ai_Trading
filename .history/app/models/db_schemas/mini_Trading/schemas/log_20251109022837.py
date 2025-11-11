from enum import Enum
from sqlalchemy import Table, Column, Integer, String

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Log(SQLAlchemyBase):


    
