from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class TeachingTask(Base):
    __tablename__ = "teaching_tasks"

    id = Column(String, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    language = Column(String, nullable=False)  # "mr", "hi", "en"
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    teacher = relationship("Teacher")
    class_ = relationship("Class")
