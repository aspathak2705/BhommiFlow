from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    source_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    state = Column(String, nullable=False, default="National")
    source_url = Column(String, nullable=True)
    document_type = Column(String, nullable=False)  # circular, manual, notification, notification_faq, FAQ
    publication_date = Column(String, nullable=True)
    effective_date = Column(String, nullable=True)
    language = Column(String, nullable=False, default="en")
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE, ARCHIVED, INVALID
    retrieved_at = Column(DateTime(timezone=True), server_default=func.now())

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    chunk_id = Column(String, primary_key=True, index=True)
    source_id = Column(String, nullable=False)
    chunk_text = Column(String, nullable=False)
    page_number = Column(String, nullable=True)
    section = Column(String, nullable=True)
