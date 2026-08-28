from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str  # "citizen" or "officer"
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = "en"
    # Officer fields
    department: Optional[str] = None
    designation: Optional[str] = None
    office: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None

class CitizenProfileResponse(BaseModel):
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    preferred_language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OfficerProfileResponse(BaseModel):
    full_name: str
    department: str
    designation: str
    office: str
    district: str
    taluka: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: str
    role: str
    citizen_profile: Optional[CitizenProfileResponse] = None
    officer_profile: Optional[OfficerProfileResponse] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str
