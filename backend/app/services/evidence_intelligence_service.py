import os
import uuid
import hashlib
import re
import json
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from app.models.evidence_intelligence import (
    BhoomiDocument, DocumentExtraction, EvidenceRecord,
    CrossRecordComparison, ConflictSignal, DocumentType,
    DocumentSourceType, ExtractionStatus, VerificationStatus,
    DifferenceType, ConflictSeverity
)
from app.models.project import Project, ProjectParcel, ProjectTimelineEvent, ActorType, DataOrigin
from app.schemas.evidence_intelligence import DocumentCreate

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

STORAGE_BASE_DIR = os.path.join(os.getcwd(), "uploads", "bhoomi_documents")
os.makedirs(STORAGE_BASE_DIR, exist_ok=True)

class DocumentStorageService:
    @staticmethod
    def save_file(file: UploadFile, project_id: str) -> Tuple[str, str, int, str]:
        # Validate MIME and extension
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}' ({file.content_type}). Allowed: PDF, PNG, JPG/JPEG.")

        content = file.file.read()
        file.file.seek(0)

        file_size = len(content)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 15MB.")

        sha256_hash = hashlib.sha256(content).hexdigest()

        # Generate safe storage path
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        project_dir = os.path.join(STORAGE_BASE_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        storage_path = os.path.join(project_dir, safe_filename)

        with open(storage_path, "wb") as f:
            f.write(content)

        return storage_path, safe_filename, file_size, sha256_hash


class NormalizationService:
    @staticmethod
    def normalize_area(raw_value: str) -> Tuple[Optional[float], Optional[str]]:
        if not raw_value:
            return None, None
        clean_text = raw_value.replace(",", "").strip()
        match = re.search(r"(\d+(?:\.\d+)?)", clean_text)
        if match:
            val = float(match.group(1))
            unit = "square_meter" if "sq" in raw_value.lower() or "m" in raw_value.lower() else "hectare"
            return val, unit
        return None, None

    @staticmethod
    def normalize_survey_number(raw_value: str) -> str:
        if not raw_value:
            return ""
        # Remove excess whitespace and normalize slashes
        return re.sub(r"\s+", "", raw_value).replace("-", "/").upper()

    @staticmethod
    def normalize_name(raw_value: str) -> str:
        if not raw_value:
            return ""
        # Collapse whitespace and convert to uppercase for normalized comparison
        clean = re.sub(r"[^\w\s]", "", raw_value)
        return " ".join(clean.split()).upper()


class EvidenceExtractionPipeline:
    @staticmethod
    def extract_and_normalize(
        db: Session, document: BhoomiDocument, raw_text_override: Optional[str] = None
    ) -> List[EvidenceRecord]:
        raw_text = raw_text_override or f"Document {document.file_name} of type {document.document_type}. Survey No: {document.survey_number or '102/4'}. Owner: Ramesh Patil. Date: 2025-03-10."
        
        extraction = DocumentExtraction(
            extraction_id=f"EXT-{uuid.uuid4().hex[:12].upper()}",
            document_id=document.document_id,
            extraction_version=1,
            raw_text=raw_text,
            structured_data_json=json.dumps({
                "survey_number": document.survey_number or "102/4",
                "subdivision_number": document.subdivision_number or "1",
                "document_number": document.document_number or "DOC-99881",
                "owner_name": "Ramesh Patil",
                "area": "1,250.50 Sq. M."
            }),
            confidence=0.95,
            status=ExtractionStatus.COMPLETED.value,
            extractor_type="PDFExtractor",
            extractor_version="1.0.0"
        )
        db.add(extraction)

        # Create structured evidence items
        evidence_items = []

        # 1. Survey Number
        surv_raw = document.survey_number or "102/4"
        ev_survey = EvidenceRecord(
            evidence_id=f"EVD-{uuid.uuid4().hex[:12].upper()}",
            document_id=document.document_id,
            project_id=document.project_id,
            parcel_id=document.parcel_id,
            evidence_type="Survey Number",
            field_name="survey_number",
            raw_value=surv_raw,
            normalized_value=NormalizationService.normalize_survey_number(surv_raw),
            source_page=1,
            confidence=0.96,
            verification_status=VerificationStatus.UNVERIFIED.value,
            data_origin="synthetic"
        )
        evidence_items.append(ev_survey)

        # 2. Owner Name
        owner_raw = "Ramesh Patil"
        ev_owner = EvidenceRecord(
            evidence_id=f"EVD-{uuid.uuid4().hex[:12].upper()}",
            document_id=document.document_id,
            project_id=document.project_id,
            parcel_id=document.parcel_id,
            evidence_type="Person Name",
            field_name="owner_name",
            raw_value=owner_raw,
            normalized_value=NormalizationService.normalize_name(owner_raw),
            source_page=1,
            confidence=0.92,
            verification_status=VerificationStatus.UNVERIFIED.value,
            data_origin="synthetic"
        )
        evidence_items.append(ev_owner)

        for ev in evidence_items:
            db.add(ev)

        document.extraction_status = ExtractionStatus.COMPLETED.value
        db.commit()
        return evidence_items


class EvidenceComparisonService:
    @staticmethod
    def compare_documents(
        db: Session, project_id: str, doc_a: BhoomiDocument, doc_b: BhoomiDocument
    ) -> List[CrossRecordComparison]:
        ev_a_list = db.query(EvidenceRecord).filter(EvidenceRecord.document_id == doc_a.document_id).all()
        ev_b_list = db.query(EvidenceRecord).filter(EvidenceRecord.document_id == doc_b.document_id).all()

        map_a = {ev.field_name: ev for ev in ev_a_list}
        map_b = {ev.field_name: ev for ev in ev_b_list}

        all_fields = set(map_a.keys()).union(set(map_b.keys()))
        comparisons = []

        for field in all_fields:
            ev_a = map_a.get(field)
            ev_b = map_b.get(field)

            val_a_raw = ev_a.raw_value if ev_a else None
            val_b_raw = ev_b.raw_value if ev_b else None
            val_a_norm = ev_a.normalized_value if ev_a else None
            val_b_norm = ev_b.normalized_value if ev_b else None

            if not ev_a:
                diff_type = DifferenceType.MISSING_IN_A.value
                sev = ConflictSeverity.MEDIUM.value
                req = True
            elif not ev_b:
                diff_type = DifferenceType.MISSING_IN_B.value
                sev = ConflictSeverity.MEDIUM.value
                req = True
            elif val_a_raw == val_b_raw:
                diff_type = DifferenceType.EXACT_MATCH.value
                sev = ConflictSeverity.LOW.value
                req = False
            elif val_a_norm == val_b_norm:
                diff_type = DifferenceType.FORMATTING_DIFFERENCE.value
                sev = ConflictSeverity.LOW.value
                req = False
            else:
                diff_type = DifferenceType.SUBSTANTIVE_CONFLICT.value
                sev = ConflictSeverity.HIGH.value
                req = True

            comp = CrossRecordComparison(
                comparison_id=f"CMP-{uuid.uuid4().hex[:12].upper()}",
                project_id=project_id,
                document_a_id=doc_a.document_id,
                document_b_id=doc_b.document_id,
                comparison_type="Document Comparison",
                field_name=field,
                value_a=val_a_raw,
                value_b=val_b_raw,
                difference_type=diff_type,
                severity=sev,
                review_required=req
            )
            db.add(comp)
            comparisons.append(comp)

            # Generate ConflictSignal for substantive differences
            if req and diff_type == DifferenceType.SUBSTANTIVE_CONFLICT.value:
                conflict = ConflictSignal(
                    conflict_id=f"CNF-{uuid.uuid4().hex[:12].upper()}",
                    project_id=project_id,
                    comparison_id=comp.comparison_id,
                    title=f"Discrepancy in {field.replace('_', ' ').title()}",
                    description=f"Document A ({doc_a.file_name}) specifies '{val_a_raw}' while Document B ({doc_b.file_name}) specifies '{val_b_raw}'. Officer review recommended.",
                    severity=sev,
                    status="Open",
                    review_required=True,
                    data_origin="synthetic"
                )
                db.add(conflict)

        db.commit()
        return comparisons


def create_document_record(
    db: Session,
    project_id: str,
    doc_in: DocumentCreate,
    file: UploadFile,
    uploader_id: Optional[str] = None
) -> BhoomiDocument:
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    storage_ref, safe_filename, file_size, sha256_hash = DocumentStorageService.save_file(file, project_id)

    doc_id = f"DOC-{uuid.uuid4().hex[:12].upper()}"
    db_doc = BhoomiDocument(
        document_id=doc_id,
        project_id=project_id,
        parcel_id=doc_in.parcel_id,
        document_type=doc_in.document_type,
        source_type=doc_in.source_type or DocumentSourceType.SYNTHETIC.value,
        file_name=file.filename or safe_filename,
        storage_reference=storage_ref,
        mime_type=file.content_type or "application/pdf",
        file_size=file_size,
        sha256_hash=sha256_hash,
        document_number=doc_in.document_number,
        registration_number=doc_in.registration_number,
        survey_number=doc_in.survey_number,
        subdivision_number=doc_in.subdivision_number,
        issuer=doc_in.issuer,
        issue_date=doc_in.issue_date,
        registration_date=doc_in.registration_date,
        transaction_date=doc_in.transaction_date,
        uploaded_by=uploader_id,
        data_origin="synthetic"
    )
    db.add(db_doc)

    # Log project timeline event
    evt = ProjectTimelineEvent(
        event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        project_id=project_id,
        parcel_id=doc_in.parcel_id,
        event_type="Document Uploaded",
        stage=project.current_stage,
        description=f"Document '{db_doc.file_name}' ({db_doc.document_type}) uploaded to project.",
        actor_type=ActorType.OFFICER.value if uploader_id else ActorType.SYSTEM.value,
        actor_id=uploader_id,
        status="COMPLETED",
        data_origin="synthetic"
    )
    db.add(evt)

    db.commit()
    db.refresh(db_doc)

    # Run extraction pipeline automatically
    EvidenceExtractionPipeline.extract_and_normalize(db, db_doc)

    # Trigger cross-record comparison if other documents exist in project
    other_docs = db.query(BhoomiDocument).filter(
        BhoomiDocument.project_id == project_id,
        BhoomiDocument.document_id != db_doc.document_id
    ).all()
    for other in other_docs:
        EvidenceComparisonService.compare_documents(db, project_id, other, db_doc)

    return db_doc
