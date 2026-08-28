from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvidenceRequestCreate(BaseModel):
    description: str

class EvidenceRequestResponse(BaseModel):
    request_id: str
    case_id: str
    requested_by: Optional[str] = None
    description: str
    status: str
    created_at: datetime
    fulfilled_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    notification_id: str
    user_id: str
    case_id: str
    channel: str
    event_type: str
    message: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
