from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConflictResponse(BaseModel):
    conflict_id: str
    case_id: str
    conflict_type: str
    severity: str
    description: str
    status: str
    source_entity_a: Optional[str] = None
    source_entity_b: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True

class ConflictStatusUpdate(BaseModel):
    status: str  # OPEN, REVIEWED, DISMISSED
