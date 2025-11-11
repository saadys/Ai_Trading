from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from schemas import SQLAlchemyBase
import uuid

class Log(SQLAlchemyBase):
    __tablename__ = 'project'
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    
    project_uuid = Column(UUID(as_uuid=True),default=uuid.uuid4, unique=True,nullable=False)

    project_name = Column(String, nullable=False)