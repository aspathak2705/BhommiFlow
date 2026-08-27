from sqlalchemy import Column, String, DateTime, func
from app.core.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
