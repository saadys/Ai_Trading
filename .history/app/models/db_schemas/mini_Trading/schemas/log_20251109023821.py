from sqlalchemy import Column, Integer, String, DateTime as SQLAlchemyEnum
from schemas import SQLAlchemyBase
from enum import Enum
import datetime

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Log(SQLAlchemyBase):

    __tablename__ = 'Logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    level = Column(SQLAlchemyEnum(LogLevel), nullable=False)
    message = Column(String, nullable=False)
    module = Column(String)
    funcName = Column(String)
    lineNo = Column(Integer)

    pass


    
