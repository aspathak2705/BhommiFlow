import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.case import Case, CaseEvent
from app.models.document import Document, Evidence
from app.schemas.case import CaseCreate, CaseResponse, CaseStatusUpdate, CaseEventResponse
from app.schemas.document import DocumentResponse, EvidenceResponse, DocumentCompareResponse
from app.schemas.conflict import ConflictResponse, ConflictStatusUpdate
from app.schemas.graph import GraphResponse
from app.services import case_service
from app.services.storage_service import storage_service
from app.services.integrity_service import calculate_sha256
from app.services.extraction_service import extract_metadata_from_text
from app.services.graph_service import build_case_graph
from app.services.conflict_service import ConflictDetectionService
from app.models.conflict import PotentialConflict
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import RAGService
from app.schemas.workflow import EvidenceRequestCreate, EvidenceRequestResponse, NotificationResponse
from app.models.workflow import EvidenceRequest, Notification
from app.services.notification_service import NotificationService

router = APIRouter()

def check_case_access(case_id: str, current_user: User, db: Session) -> Case:
    case_obj = case_service.get_case(db=db, case_id=case_id)
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    if current_user.role == "citizen" and case_obj.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this case")
    if current_user.role == "officer" and case_obj.assigned_officer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this case")
    return case_obj

@router.post("/cases", response_model=CaseResponse)
def create_case(case_in: CaseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "citizen":
        raise HTTPException(status_code=403, detail="Only citizens can create cases")
    return case_service.create_case(db=db, case_in=case_in, citizen_id=current_user.id)

@router.get("/cases", response_model=List[CaseResponse])
def get_cases(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "citizen":
        return case_service.list_citizen_cases(db=db, citizen_id=current_user.id)
    elif current_user.role == "officer":
        return case_service.list_officer_cases(db=db, officer_id=current_user.id)
    return []

@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return check_case_access(case_id, current_user, db)

@router.patch("/cases/{case_id}/status", response_model=CaseResponse)
def update_case_status(
    case_id: str, 
    status_update: CaseStatusUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    case_obj = check_case_access(case_id, current_user, db)
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can update case status")
        
    updated = case_service.update_case_status(
        db=db, 
        case_id=case_id, 
        status_update=status_update, 
        actor_id=current_user.id, 
        actor_role=current_user.role
    )
    return updated

@router.get("/cases/{case_id}/events", response_model=List[CaseEventResponse])
def get_case_events(case_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_case_access(case_id, current_user, db)
    return db.query(CaseEvent).filter(CaseEvent.case_id == case_id).order_by(CaseEvent.timestamp.asc()).all()

# --- PHASE 2 FILE UPLOAD AND INTEGRITY APIS ---

@router.post("/cases/{case_id}/documents", response_model=DocumentResponse)
def upload_document(
    case_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case_obj = check_case_access(case_id, current_user, db)
    
    # Restrict file limits (e.g. max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum permitted limit (10MB)")
        
    # Restrict permitted MIME types
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, JPEG, PNG are permitted")

    # Generate document ID and calculate hash server-side
    document_id = f"DOC-{uuid.uuid4().hex[:12].upper()}"
    sha256_hash = calculate_sha256(content)

    # Store actual file content using storage abstraction
    file_ref = storage_service.store(document_id, file)

    # Process rule-based extraction
    try:
        text_content = content.decode("utf-8", errors="ignore")
    except Exception:
        text_content = ""
    extracted = extract_metadata_from_text(text_content)
    extracted_json = json.dumps(extracted) if extracted else None

    # Persist document metadata
    db_doc = Document(
        document_id=document_id,
        case_id=case_id,
        uploaded_by=current_user.id,
        document_type=document_type,
        file_name=file.filename,
        file_reference=file_ref,
        mime_type=file.content_type,
        file_size=len(content),
        sha256_hash=sha256_hash,
        status="READY",
        extracted_metadata=extracted_json
    )
    db.add(db_doc)

    # Create evidence link
    evidence_type = "OFFICIAL_COUNTERPART" if current_user.role == "officer" else "CITIZEN_SUBMISSION"
    db_evidence = Evidence(
        evidence_id=f"EVI-{uuid.uuid4().hex[:12].upper()}",
        case_id=case_id,
        document_id=document_id,
        evidence_type=evidence_type,
        submitted_by=current_user.id,
        status="ACTIVE"
    )
    db.add(db_evidence)

    # Log case timeline evidence events
    event_type = "OFFICIAL_COUNTERPART_UPLOADED" if current_user.role == "officer" else "DOCUMENT_UPLOADED"
    case_service.log_event(
        db=db,
        case_id=case_id,
        event_type=event_type,
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={"document_id": document_id, "file_name": file.filename}
    )

    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/cases/{case_id}/evidence", response_model=List[EvidenceResponse])
def get_evidence(case_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_case_access(case_id, current_user, db)
    return db.query(Evidence).filter(Evidence.case_id == case_id).order_by(Evidence.submitted_at.desc()).all()

@router.post("/documents/{document_id}/compare", response_model=DocumentCompareResponse)
def compare_documents(
    document_id: str,
    counterpart_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can perform comparisons")

    doc_a = db.query(Document).filter(Document.document_id == document_id).first()
    doc_b = db.query(Document).filter(Document.document_id == counterpart_id).first()

    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both documents not found")

    # Authorize case access
    check_case_access(doc_a.case_id, current_user, db)
    check_case_access(doc_b.case_id, current_user, db)

    # Compare hashes
    hashes_match = doc_a.sha256_hash == doc_b.sha256_hash
    status_text = "EXACT FILE MATCH" if hashes_match else "Documents differ — review required."

    metadata_a = json.loads(doc_a.extracted_metadata) if doc_a.extracted_metadata else None
    metadata_b = json.loads(doc_b.extracted_metadata) if doc_b.extracted_metadata else None

    # Deterministic content comparison layer
    # Read files to extract text
    content_comparison_available = False
    text_diff_detected = None
    comparison_summary = None

    if not hashes_match:
        # Check if both are text/PDF format
        text_mime_types = ["application/pdf", "text/plain"]
        if doc_a.mime_type in text_mime_types and doc_b.mime_type in text_mime_types:
            try:
                # Read bytes via storage retrieval
                text_a = storage_service.retrieve(doc_a.file_reference).decode("utf-8", errors="ignore")
                text_b = storage_service.retrieve(doc_b.file_reference).decode("utf-8", errors="ignore")
                
                content_comparison_available = True
                text_diff_detected = text_a.strip() != text_b.strip()
                if text_diff_detected:
                    comparison_summary = "Character difference detected in extracted text content."
                else:
                    comparison_summary = "Extracted text content matches despite different digital file signatures."
            except Exception as e:
                comparison_summary = f"Content comparison error: {str(e)}. Requiring officer visual review."
        else:
            comparison_summary = "Content comparison unavailable for this file format type. Requiring officer visual review."

    # Log comparison event
    case_service.log_event(
        db=db,
        case_id=doc_a.case_id,
        event_type="DOCUMENT_COMPARED",
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={
            "document_id_a": document_id,
            "document_id_b": counterpart_id,
            "match": hashes_match,
            "text_diff_detected": text_diff_detected
        }
    )

    return {
        "match": hashes_match,
        "status_text": status_text,
        "citizen_hash": doc_a.sha256_hash,
        "officer_hash": doc_b.sha256_hash,
        "citizen_metadata": metadata_a,
        "officer_metadata": metadata_b,
        "content_comparison_available": content_comparison_available,
        "text_diff_detected": text_diff_detected,
        "comparison_summary": comparison_summary
    }

@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Enforce case access authorization check
    check_case_access(doc.case_id, current_user, db)
    
    # Securely retrieve file contents
    try:
        content = storage_service.retrieve(doc.file_reference)
    except Exception:
        raise HTTPException(status_code=404, detail="File content missing from storage")
        
    from fastapi.responses import Response
    return Response(content=content, media_type=doc.mime_type)

# --- PHASE 3 CASE GRAPH & CONFLICT DETECTION APIS ---

@router.get("/cases/{case_id}/graph", response_model=GraphResponse)
def get_case_graph(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_case_access(case_id, current_user, db)
    return build_case_graph(db, case_id)

@router.post("/cases/{case_id}/conflicts/analyze")
def analyze_case_conflicts(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_case_access(case_id, current_user, db)
    # Re-run deterministic conflict rules
    ConflictDetectionService.analyze_case_conflicts(db, case_id)
    return {"status": "success", "message": "Conflict evaluation finished"}

@router.get("/cases/{case_id}/conflicts", response_model=List[ConflictResponse])
def get_case_conflicts(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_case_access(case_id, current_user, db)
    # Automatically execute analysis to fetch up-to-date potential conflicts
    ConflictDetectionService.analyze_case_conflicts(db, case_id)
    return db.query(PotentialConflict).filter(PotentialConflict.case_id == case_id).all()

@router.patch("/conflicts/{conflict_id}/status", response_model=ConflictResponse)
def update_conflict_status(
    conflict_id: str,
    status_update: ConflictStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can update conflict review statuses")
        
    conflict = db.query(PotentialConflict).filter(PotentialConflict.conflict_id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict record not found")
        
    # Enforce case authorization check
    check_case_access(conflict.case_id, current_user, db)
    
    conflict.status = status_update.status
    if status_update.status in ["REVIEWED", "DISMISSED"]:
        conflict.reviewed_by = current_user.id
        from datetime import datetime, timezone
        conflict.resolved_at = datetime.now(timezone.utc)
        
    # Log timeline activity review event
    case_service.log_event(
        db=db,
        case_id=conflict.case_id,
        event_type="CONFLICT_REVIEWED" if status_update.status == "REVIEWED" else "CONFLICT_DISMISSED",
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={"conflict_id": conflict_id, "status": status_update.status}
    )
    
    db.commit()
    db.refresh(conflict)
    return conflict

# --- PHASE 4 PROCEDURE RAG & GROUNDED INTELLIGENCE APIS ---

@router.post("/cases/{case_id}/guidance", response_model=RAGQueryResponse)
def get_case_guidance(
    case_id: str,
    query_in: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Enforce case scope access authorization
    case_obj = check_case_access(case_id, current_user, db)
    
    # Populate case context
    case_context = {
        "case_type": case_obj.case_type,
        "description": case_obj.description,
        "district": case_obj.district,
        "taluka": case_obj.taluka,
        "village": case_obj.village
    }
    
    # Execute grounded RAG query
    result = RAGService.generate_grounded_guidance(
        db=db,
        case_context=case_context,
        user_question=query_in.question,
        role=current_user.role
    )
    return result

# --- PHASE 5 EVIDENCE REQUESTS & NOTIFICATION APIS ---

@router.post("/cases/{case_id}/evidence-requests", response_model=EvidenceRequestResponse)
def create_evidence_request(
    case_id: str,
    req_in: EvidenceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can request additional evidence")
        
    case_obj = check_case_access(case_id, current_user, db)
    
    # Save request record
    req_id = f"ERQ-{uuid.uuid4().hex[:12].upper()}"
    db_req = EvidenceRequest(
        request_id=req_id,
        case_id=case_id,
        requested_by=current_user.id,
        description=req_in.description,
        status="OPEN"
    )
    db.add(db_req)
    
    # Force state mutation to ACTION_REQUIRED
    case_obj.status = "ACTION_REQUIRED"
    
    # Log timeline event
    case_service.log_event(
        db=db,
        case_id=case_id,
        event_type="EVIDENCE_REQUESTED",
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={"request_id": req_id, "description": req_in.description}
    )
    case_service.log_event(
        db=db,
        case_id=case_id,
        event_type="STATUS_CHANGED",
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={"old_status": "UNDER_REVIEW", "new_status": "ACTION_REQUIRED", "note": f"Requested: {req_in.description}"}
    )
    
    # Trigger SMS notification event
    sms_msg = f"BhoomiFlow: Additional evidence requested for Case {case_obj.case_reference}. Description: {req_in.description}. Please log in to upload."
    NotificationService.send_sms(db, user_id=case_obj.citizen_id, case_id=case_id, event_type="EVIDENCE_REQUESTED", message=sms_msg)
    
    db.commit()
    db.refresh(db_req)
    return db_req

@router.get("/cases/{case_id}/evidence-requests", response_model=List[EvidenceRequestResponse])
def get_case_evidence_requests(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_case_access(case_id, current_user, db)
    return db.query(EvidenceRequest).filter(EvidenceRequest.case_id == case_id).order_by(EvidenceRequest.created_at.desc()).all()

@router.post("/evidence-requests/{request_id}/fulfill")
def fulfill_evidence_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(EvidenceRequest).filter(EvidenceRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Evidence request not found")
        
    case_obj = check_case_access(req.case_id, current_user, db)
    if current_user.role != "citizen" or case_obj.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the case owner can fulfill evidence requests")
        
    req.status = "FULFILLED"
    from datetime import datetime, timezone
    req.fulfilled_at = datetime.now(timezone.utc)
    
    # Update case status to RESUBMITTED
    case_obj.status = "RESUBMITTED"
    
    # Log timeline event
    case_service.log_event(
        db=db,
        case_id=req.case_id,
        event_type="STATUS_CHANGED",
        actor_id=current_user.id,
        actor_role=current_user.role,
        metadata={"old_status": "ACTION_REQUIRED", "new_status": "RESUBMITTED", "note": "Citizen fulfilled evidence request"}
    )
    
    # Trigger SMS notification event
    if case_obj.assigned_officer_id:
        sms_msg = f"BhoomiFlow: Citizen has submitted requested evidence for Case {case_obj.case_reference}."
        NotificationService.send_sms(db, user_id=case_obj.assigned_officer_id, case_id=req.case_id, event_type="EVIDENCE_RECEIVED", message=sms_msg)
        
    db.commit()
    return {"status": "success", "message": "Evidence request marked as fulfilled"}

@router.get("/cases/{case_id}/notifications", response_model=List[NotificationResponse])
def get_case_notifications(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_case_access(case_id, current_user, db)
    return db.query(Notification).filter(Notification.case_id == case_id).order_by(Notification.created_at.desc()).all()

