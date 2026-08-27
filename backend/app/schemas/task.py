from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal

class TeachingTaskBase(BaseModel):
    subject: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0)
    language: Literal["en", "hi", "mr"]

class TeachingTaskCreate(TeachingTaskBase):
    teacher_id: str
    class_id: str

class TeachingTaskUpdate(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    language: Optional[Literal["en", "hi", "mr"]] = None
    status: Optional[str] = None

class TeachingTaskResponse(TeachingTaskBase):
    id: str
    teacher_id: str
    class_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
