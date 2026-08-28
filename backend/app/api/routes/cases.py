from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.case import CaseEvent
from app.schemas.case import CaseCreate, CaseResponse, CaseStatusUpdate, CaseEventResponse
from app.services import case_service

router = APIRouter()

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
    case_obj = case_service.get_case(db=db, case_id=case_id)
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Auth checks
    if current_user.role == "citizen" and case_obj.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case")
    if current_user.role == "officer" and case_obj.assigned_officer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case")
    
    return case_obj

@router.patch("/cases/{case_id}/status", response_model=CaseResponse)
def update_case_status(
    case_id: str, 
    status_update: CaseStatusUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    case_obj = case_service.get_case(db=db, case_id=case_id)
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can update case status")
    if case_obj.assigned_officer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this case")
        
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
    case_obj = case_service.get_case(db=db, case_id=case_id)
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if current_user.role == "citizen" and case_obj.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access these events")
    if current_user.role == "officer" and case_obj.assigned_officer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access these events")
        
    return db.query(CaseEvent).filter(CaseEvent.case_id == case_id).order_by(CaseEvent.timestamp.asc()).all()
