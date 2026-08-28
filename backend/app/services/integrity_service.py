import hashlib
from sqlalchemy.orm import Session
from app.models.case import CaseEvent

def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def compute_canonical_event_hash(prev_hash: str, event: CaseEvent) -> str:
    # Format: previous_hash:event_id:event_type:case_id:actor_role:timestamp
    prev = prev_hash if prev_hash else "GENESIS"
    timestamp_str = str(event.timestamp) if event.timestamp else "NOW"
    raw_data = f"{prev}:{event.event_id}:{event.event_type}:{event.case_id}:{event.actor_role}:{timestamp_str}"
    return calculate_sha256(raw_data.encode("utf-8"))

def append_to_hash_chain(db: Session, event: CaseEvent) -> CaseEvent:
    # Find the immediately preceding event for this case
    prev_event = (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == event.case_id, CaseEvent.event_id != event.event_id)
        .order_by(CaseEvent.timestamp.desc(), CaseEvent.event_id.desc())
        .first()
    )
    
    prev_hash = prev_event.current_event_hash if prev_event else None
    event.previous_event_hash = prev_hash
    event.current_event_hash = compute_canonical_event_hash(prev_hash, event)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def verify_hash_chain(db: Session, case_id: str) -> bool:
    events = (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.timestamp.asc(), CaseEvent.event_id.asc())
        .all()
    )
    
    expected_prev = None
    for event in events:
        if event.previous_event_hash != expected_prev:
            return False
            
        computed = compute_canonical_event_hash(expected_prev, event)
        if event.current_event_hash != computed:
            return False
            
        expected_prev = event.current_event_hash
        
    return True
