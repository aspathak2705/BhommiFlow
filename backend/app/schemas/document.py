from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    document_id: str
    case_id: str
    uploaded_by: str
    document_type: str
    file_name: str
    file_size: int
    sha256_hash: str
    uploaded_at: datetime
    status: str
    extracted_metadata: Optional[str] = None

    class Config:
        from_attributes = True

class EvidenceResponse(BaseModel):
    evidence_id: str
    case_id: str
    document_id: str
    evidence_type: str
    submitted_by: str
    submitted_at: datetime
    status: str
    document: DocumentResponse

    class Config:
        from_attributes = True

class DocumentCompareResponse(BaseModel):
    match: bool
    status_text: str
    citizen_hash: str
    officer_hash: str
    citizen_metadata: Optional[dict] = None
    officer_metadata: Optional[dict] = None
    content_comparison_available: bool
    text_diff_detected: Optional[bool] = None
    comparison_summary: Optional[str] = None
