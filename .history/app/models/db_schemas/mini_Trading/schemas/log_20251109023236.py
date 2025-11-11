from sqlalchemy import Table, Column, Integer, String
from schemas import SQLAlchemyBase
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Log(SQLAlchemyBase):

    __tablename__ = 'Logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timetamp =

    pass


    
