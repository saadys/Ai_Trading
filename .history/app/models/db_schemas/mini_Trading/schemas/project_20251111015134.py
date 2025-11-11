from sqlalchemy import Column, Integer, String, DateTime
from schemas import SQLAlchemyBase


class Log(SQLAlchemyBase):
    __tablename__ = 'project'
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    
    project
