from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Class(Base):
    __tablename__ = "classes"

    id = Column(String, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    section = Column(String, nullable=False)
    primary_language = Column(String, nullable=False)  # e.g., "mr", "hi", "en"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    teacher = relationship("Teacher")
