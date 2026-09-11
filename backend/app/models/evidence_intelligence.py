from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class DocumentType(str, Enum):
    EXTRACT_7_12 = "7/12 Extract"
    EXTRACT_8A = "8A Extract"
    PROPERTY_CARD = "Property Card"
    SALE_DEED = "Sale Deed"
    MUTATION_RECORD = "Mutation Record"
    REGISTRATION_RECORD = "Registration Record"
    COURT_ORDER = "Court Order"
    DEATH_CERTIFICATE = "Death Certificate"
    LEGAL_HEIR_RECORD = "Legal Heir Record"
    SUCCESSION_RECORD = "Succession Record"
    SURVEY_RECORD = "Survey Record"
    COMPENSATION_RECORD = "Compensation Record"
    AWARD = "Award"
    POSSESSION_RECORD = "Possession Record"
    RR_RECORD = "R&R Record"
    OTHER = "Other"

class DocumentSourceType(str, Enum):
    USER_SUBMITTED = "user_submitted"
    GOVERNMENT_SOURCE = "government_source"
    SYSTEM_IMPORTED = "system_imported"
    SYNTHETIC = "synthetic"

class ExtractionStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    NEEDS_REVIEW = "Needs Review"
    FAILED = "Failed"

class VerificationStatus(str, Enum):
    UNVERIFIED = "Unverified"
    SYSTEM_REVIEWED = "System Reviewed"
    OFFICER_VERIFIED = "Officer Verified"
    REJECTED = "Rejected"

class DifferenceType(str, Enum):
    EXACT_MATCH = "Exact Match"
    FORMATTING_DIFFERENCE = "Formatting Difference"
    NORMALIZATION_DIFFERENCE = "Normalization Difference"
    POSSIBLE_IDENTITY_VARIATION = "Possible Identity Variation"
    SUBSTANTIVE_CONFLICT = "Substantive Conflict"
    MISSING_IN_A = "Missing in A"
    MISSING_IN_B = "Missing in B"

class ConflictSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class BhoomiDocument(Base):
    __tablename__ = "bhoomi_documents"

    document_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    parcel_id = Column(String, ForeignKey("project_parcels.parcel_id", ondelete="SET NULL"), nullable=True, index=True)

    document_type = Column(String, nullable=False, index=True)
    source_type = Column(String, nullable=False, default=DocumentSourceType.SYNTHETIC.value)

    file_name = Column(String, nullable=False)
    storage_reference = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False, index=True)
    page_count = Column(Integer, nullable=False, default=1)

    document_number = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    survey_number = Column(String, nullable=True)
    subdivision_number = Column(String, nullable=True)
    issuer = Column(String, nullable=True)

    issue_date = Column(DateTime(timezone=True), nullable=True)
    registration_date = Column(DateTime(timezone=True), nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=True)

    document_status = Column(String, nullable=False, default="ACTIVE")
    extraction_status = Column(String, nullable=False, default=ExtractionStatus.PENDING.value, index=True)

    uploaded_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    parcel = relationship("ProjectParcel")
    uploader = relationship("User")

    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceRecord", back_populates="document", cascade="all, delete-orphan")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    extraction_id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("bhoomi_documents.document_id", ondelete="CASCADE"), nullable=False, index=True)
    extraction_version = Column(Integer, nullable=False, default=1)

    raw_text = Column(Text, nullable=True)
    structured_data_json = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)

    status = Column(String, nullable=False, default=ExtractionStatus.COMPLETED.value)
    extractor_type = Column(String, nullable=False, default="TextExtractor")
    extractor_version = Column(String, nullable=False, default="1.0.0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("BhoomiDocument", back_populates="extractions")


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    evidence_id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("bhoomi_documents.document_id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    parcel_id = Column(String, ForeignKey("project_parcels.parcel_id", ondelete="SET NULL"), nullable=True, index=True)

    evidence_type = Column(String, nullable=False, index=True)  # e.g., Survey Number, Person Name
    field_name = Column(String, nullable=False, index=True)
    raw_value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=True)

    source_page = Column(Integer, nullable=False, default=1)
    confidence = Column(Float, nullable=False, default=1.0)
    verification_status = Column(String, nullable=False, default=VerificationStatus.UNVERIFIED.value)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    document = relationship("BhoomiDocument", back_populates="evidence_items")
    project = relationship("Project")
    parcel = relationship("ProjectParcel")


class CrossRecordComparison(Base):
    __tablename__ = "cross_record_comparisons"

    comparison_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    document_a_id = Column(String, ForeignKey("bhoomi_documents.document_id", ondelete="CASCADE"), nullable=False, index=True)
    document_b_id = Column(String, ForeignKey("bhoomi_documents.document_id", ondelete="CASCADE"), nullable=False, index=True)

    comparison_type = Column(String, nullable=False, default="Document Comparison")
    field_name = Column(String, nullable=False)

    value_a = Column(Text, nullable=True)
    value_b = Column(Text, nullable=True)

    difference_type = Column(String, nullable=False)
    severity = Column(String, nullable=False, default=ConflictSeverity.LOW.value)
    review_required = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")
    document_a = relationship("BhoomiDocument", foreign_keys=[document_a_id])
    document_b = relationship("BhoomiDocument", foreign_keys=[document_b_id])


class ConflictSignal(Base):
    __tablename__ = "conflict_signals"

    conflict_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    comparison_id = Column(String, ForeignKey("cross_record_comparisons.comparison_id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False, default=ConflictSeverity.MEDIUM.value, index=True)
    status = Column(String, nullable=False, default="Open")
    review_required = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    comparison = relationship("CrossRecordComparison")
