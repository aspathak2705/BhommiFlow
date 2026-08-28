import uuid
import json
from sqlalchemy.orm import Session
from app.models.case import Case, LandParcel, Person, CasePerson, CaseEvent
from app.models.user import User
from app.schemas.case import CaseCreate, CaseStatusUpdate

def generate_case_reference(db: Session) -> str:
    # Format: BF-2026-XXXXXXXX
    # Generates a random 8-character uppercase hex string
    import random
    import string
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    ref = f"BF-2026-{chars}"
    
    # Ensure uniqueness
    while db.query(Case).filter(Case.case_reference == ref).first() is not None:
        chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        ref = f"BF-2026-{chars}"
    return ref

def create_case(db: Session, case_in: CaseCreate, citizen_id: str) -> Case:
    case_id = f"CASE-{uuid.uuid4().hex[:12].upper()}"
    ref = generate_case_reference(db)

    db_case = Case(
        case_id=case_id,
        case_reference=ref,
        citizen_id=citizen_id,
        case_type=case_in.case_type,
        title=case_in.title,
        description=case_in.description,
        status="SUBMITTED",
        priority=case_in.priority,
        district=case_in.district,
        taluka=case_in.taluka,
        village=case_in.village,
    )
    db.add(db_case)

    # Add land parcels
    for lp in case_in.land_parcels:
        db_lp = LandParcel(
            id=f"LP-{uuid.uuid4().hex[:12].upper()}",
            case_id=case_id,
            district=lp.district,
            taluka=lp.taluka,
            village=lp.village,
            survey_number=lp.survey_number,
            subdivision_number=lp.subdivision_number,
            property_type=lp.property_type,
            area=lp.area,
            area_unit=lp.area_unit,
            description=lp.description,
        )
        db.add(db_lp)

    # Add people involved
    for p in case_in.people:
        person_id = f"PER-{uuid.uuid4().hex[:12].upper()}"
        db_p = Person(
            id=person_id,
            full_name=p.full_name,
            phone=p.phone,
            email=p.email,
            address=p.address,
        )
        db.add(db_p)

        db_cp = CasePerson(
            id=f"CP-{uuid.uuid4().hex[:12].upper()}",
            case_id=case_id,
            person_id=person_id,
            role=p.role,
            notes=p.notes,
        )
        db.add(db_cp)

    # Log timeline event
    log_event(db, case_id=case_id, event_type="CASE_CREATED", actor_id=citizen_id, actor_role="citizen")
    log_event(db, case_id=case_id, event_type="CASE_SUBMITTED", actor_id=citizen_id, actor_role="citizen")

    db.commit()
    db.refresh(db_case)
    return db_case

def log_event(db: Session, case_id: str, event_type: str, actor_id: str, actor_role: str, metadata: dict = None) -> CaseEvent:
    event_id = f"EVT-{uuid.uuid4().hex[:12].upper()}"
    db_event = CaseEvent(
        event_id=event_id,
        case_id=case_id,
        event_type=event_type,
        actor_id=actor_id,
        actor_role=actor_role,
        metadata_json=json.dumps(metadata) if metadata else None
    )
    db.add(db_event)
    return db_event

def get_case(db: Session, case_id: str) -> Case:
    return db.query(Case).filter(Case.case_id == case_id).first()

def list_citizen_cases(db: Session, citizen_id: str) -> list[Case]:
    return db.query(Case).filter(Case.citizen_id == citizen_id).order_by(Case.created_at.desc()).all()

def list_officer_cases(db: Session, officer_id: str) -> list[Case]:
    return db.query(Case).filter(Case.assigned_officer_id == officer_id).order_by(Case.created_at.desc()).all()

def update_case_status(db: Session, case_id: str, status_update: CaseStatusUpdate, actor_id: str, actor_role: str) -> Case:
    db_case = get_case(db, case_id)
    if not db_case:
        return None

    old_status = db_case.status
    db_case.status = status_update.status
    
    metadata = {"old_status": old_status, "new_status": status_update.status}
    if status_update.note:
        metadata["note"] = status_update.note

    log_event(db, case_id=case_id, event_type="STATUS_CHANGED", actor_id=actor_id, actor_role=actor_role, metadata=metadata)
    db.commit()
    db.refresh(db_case)
    return db_case
