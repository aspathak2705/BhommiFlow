from pydantic import BaseModel
from datetime import datetime

class TeacherBase(BaseModel):
    name: str

class TeacherCreate(TeacherBase):
    id: str

class TeacherResponse(TeacherBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
