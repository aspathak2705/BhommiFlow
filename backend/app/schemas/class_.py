from pydantic import BaseModel
from datetime import datetime

class ClassBase(BaseModel):
    name: str
    grade: str
    section: str
    primary_language: str

class ClassCreate(ClassBase):
    id: str
    teacher_id: str

class ClassResponse(ClassBase):
    id: str
    teacher_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
