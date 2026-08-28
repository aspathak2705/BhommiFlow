from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String, nullable=False)  # Sale Deed, Mutation Document, Property Card, etc.
    file_name = Column(String, nullable=False)
    file_reference = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, default="UPLOADED")  # UPLOADED, PROCESSING, READY, REVIEW_REQUIRED
    extracted_metadata = Column(String, nullable=True)  # JSON-serialized metadata string

    case = relationship("Case", back_populates="documents")
    uploader = relationship("User")

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String, nullable=False)  # CITIZEN_SUBMISSION, OFFICIAL_COUNTERPART
    submitted_by = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE, SUPERSEDED, REVIEWED

    case = relationship("Case", back_populates="evidence")
    document = relationship("Document")
    submitter = relationship("User")
