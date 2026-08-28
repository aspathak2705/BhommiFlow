from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Land Parcel schemas
class LandParcelBase(BaseModel):
    district: str
    taluka: str
    village: str
    survey_number: Optional[str] = None
    subdivision_number: Optional[str] = None
    property_type: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    description: Optional[str] = None

class LandParcelCreate(LandParcelBase):
    pass

class LandParcelResponse(LandParcelBase):
    id: str
    case_id: str

    class Config:
        from_attributes = True

# Person involved schemas
class PersonBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PersonCreate(PersonBase):
    role: str  # owner, heir, buyer, seller, applicant, other
    notes: Optional[str] = None

class PersonResponse(PersonBase):
    id: str

    class Config:
        from_attributes = True

class CasePersonResponse(BaseModel):
    id: str
    role: str
    notes: Optional[str]
    person: PersonResponse

    class Config:
        from_attributes = True

# Case Event schemas
class CaseEventResponse(BaseModel):
    event_id: str
    case_id: str
    event_type: str
    actor_id: Optional[str]
    actor_role: str
    timestamp: datetime
    metadata_json: Optional[str]
    previous_event_hash: Optional[str]
    current_event_hash: Optional[str]

    class Config:
        from_attributes = True

# Case schemas
class CaseBase(BaseModel):
    case_type: str
    title: str
    description: str
    priority: str = "MEDIUM"
    district: str
    taluka: str
    village: str

class CaseCreate(CaseBase):
    land_parcels: List[LandParcelCreate] = []
    people: List[PersonCreate] = []

class CaseStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None

class CaseResponse(CaseBase):
    case_id: str
    case_reference: str
    citizen_id: str
    assigned_officer_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    land_parcels: List[LandParcelResponse] = []
    people: List[CasePersonResponse] = []

    class Config:
        from_attributes = True
