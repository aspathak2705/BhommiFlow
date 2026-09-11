from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentCreate(BaseModel):
    document_type: str = Field(..., description="Type of land document (e.g., 7/12 Extract, Sale Deed)")
    source_type: Optional[str] = Field("synthetic", description="user_submitted, government_source, synthetic")
    parcel_id: Optional[str] = Field(None, description="Optional associated parcel ID")
    document_number: Optional[str] = None
    registration_number: Optional[str] = None
    survey_number: Optional[str] = None
    subdivision_number: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[datetime] = None
    registration_date: Optional[datetime] = None
    transaction_date: Optional[datetime] = None

class DocumentResponse(BaseModel):
    document_id: str
    project_id: str
    parcel_id: Optional[str] = None
    document_type: str
    source_type: str
    file_name: str
    storage_reference: str
    mime_type: str
    file_size: int
    sha256_hash: str
    page_count: int
    document_number: Optional[str] = None
    registration_number: Optional[str] = None
    survey_number: Optional[str] = None
    subdivision_number: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[datetime] = None
    registration_date: Optional[datetime] = None
    transaction_date: Optional[datetime] = None
    document_status: str
    extraction_status: str
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True

class ExtractionResponse(BaseModel):
    extraction_id: str
    document_id: str
    extraction_version: int
    raw_text: Optional[str] = None
    structured_data_json: Optional[str] = None
    confidence: float
    status: str
    extractor_type: str
    extractor_version: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EvidenceRecordResponse(BaseModel):
    evidence_id: str
    document_id: str
    project_id: str
    parcel_id: Optional[str] = None
    evidence_type: str
    field_name: str
    raw_value: str
    normalized_value: Optional[str] = None
    source_page: int
    confidence: float
    verification_status: str
    created_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True

class CrossRecordComparisonResponse(BaseModel):
    comparison_id: str
    project_id: str
    document_a_id: str
    document_b_id: str
    comparison_type: str
    field_name: str
    value_a: Optional[str] = None
    value_b: Optional[str] = None
    difference_type: str
    severity: str
    review_required: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConflictSignalResponse(BaseModel):
    conflict_id: str
    project_id: str
    comparison_id: Optional[str] = None
    title: str
    description: str
    severity: str
    status: str
    review_required: bool
    created_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True
