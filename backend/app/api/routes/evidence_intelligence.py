from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.evidence_intelligence import (
    BhoomiDocument, DocumentExtraction, EvidenceRecord,
    CrossRecordComparison, ConflictSignal
)
from app.schemas.evidence_intelligence import (
    DocumentCreate, DocumentResponse, ExtractionResponse,
    EvidenceRecordResponse, CrossRecordComparisonResponse, ConflictSignalResponse
)
from app.services import evidence_intelligence_service

router = APIRouter()

@router.post("/projects/{project_id}/documents", response_model=DocumentResponse)
def upload_project_document(
    project_id: str,
    document_type: str = Form(...),
    source_type: Optional[str] = Form("synthetic"),
    parcel_id: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    registration_number: Optional[str] = Form(None),
    survey_number: Optional[str] = Form(None),
    subdivision_number: Optional[str] = Form(None),
    issuer: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_in = DocumentCreate(
        document_type=document_type,
        source_type=source_type,
        parcel_id=parcel_id,
        document_number=document_number,
        registration_number=registration_number,
        survey_number=survey_number,
        subdivision_number=subdivision_number,
        issuer=issuer
    )
    return evidence_intelligence_service.create_document_record(
        db=db, project_id=project_id, doc_in=doc_in, file=file, uploader_id=current_user.id
    )

@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
def list_project_documents(
    project_id: str,
    document_type: Optional[str] = Query(None),
    parcel_id: Optional[str] = Query(None),
    extraction_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id)
    if document_type:
        query = query.filter(BhoomiDocument.document_type == document_type)
    if parcel_id:
        query = query.filter(BhoomiDocument.parcel_id == parcel_id)
    if extraction_status:
        query = query.filter(BhoomiDocument.extraction_status == extraction_status)
    return query.order_by(BhoomiDocument.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(BhoomiDocument).filter(BhoomiDocument.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/documents/{document_id}/extractions", response_model=List[ExtractionResponse])
def get_document_extractions(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(DocumentExtraction).filter(DocumentExtraction.document_id == document_id).order_by(DocumentExtraction.extraction_version.desc()).all()

@router.get("/projects/{project_id}/evidence", response_model=List[EvidenceRecordResponse])
def list_project_evidence(
    project_id: str,
    parcel_id: Optional[str] = Query(None),
    field_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(EvidenceRecord).filter(EvidenceRecord.project_id == project_id)
    if parcel_id:
        query = query.filter(EvidenceRecord.parcel_id == parcel_id)
    if field_name:
        query = query.filter(EvidenceRecord.field_name == field_name)
    return query.order_by(EvidenceRecord.created_at.desc()).all()

@router.get("/documents/{document_id}/evidence", response_model=List[EvidenceRecordResponse])
def list_document_evidence(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(EvidenceRecord).filter(EvidenceRecord.document_id == document_id).all()

@router.get("/projects/{project_id}/conflicts", response_model=List[ConflictSignalResponse])
def list_project_conflicts(
    project_id: str,
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id)
    if severity:
        query = query.filter(ConflictSignal.severity == severity)
    if status:
        query = query.filter(ConflictSignal.status == status)
    return query.order_by(ConflictSignal.created_at.desc()).all()

@router.get("/comparisons/{comparison_id}", response_model=CrossRecordComparisonResponse)
def get_comparison_detail(
    comparison_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(CrossRecordComparison).filter(CrossRecordComparison.comparison_id == comparison_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    return comp
