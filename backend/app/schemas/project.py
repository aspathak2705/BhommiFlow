from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ProjectParcelBase(BaseModel):
    survey_number: str
    subdivision_number: Optional[str] = None
    state: str
    district: str
    taluka: str
    village: str
    land_type: str = "Agricultural"
    area: float = Field(gt=0, description="Area must be greater than 0")
    area_unit: str = "Hectares"
    parcel_status: str = "Identified"
    geometry: Optional[str] = None

class ProjectParcelCreate(ProjectParcelBase):
    pass

class ProjectParcelResponse(ProjectParcelBase):
    parcel_id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    data_origin: str

    class Config:
        from_attributes = True


class ProjectTimelineEventResponse(BaseModel):
    event_id: str
    project_id: str
    parcel_id: Optional[str] = None
    event_type: str
    event_date: datetime
    stage: Optional[str] = None
    description: str
    actor_type: str
    actor_id: Optional[str] = None
    status: str
    metadata_json: Optional[str] = None
    created_at: datetime
    data_origin: str

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    project_name: str
    project_type: str
    project_sector: Optional[str] = None
    project_scale: str = "Medium"
    state: str
    district: str
    taluka: str
    village: str
    project_start_date: datetime
    planned_completion_date: datetime
    land_required_area: float = Field(gt=0, description="Required land area must be greater than 0")
    land_area_unit: str = "Hectares"
    affected_families: int = Field(default=0, ge=0, description="Affected families must be non-negative")
    affected_landholders: int = Field(default=0, ge=0, description="Affected landholders must be non-negative")
    project_status: str = "Draft"
    description: Optional[str] = None

    @field_validator("planned_completion_date")
    @classmethod
    def validate_dates(cls, v, info):
        if "project_start_date" in info.data and v < info.data["project_start_date"]:
            raise ValueError("planned_completion_date cannot be earlier than project_start_date")
        return v

class ProjectCreate(ProjectBase):
    parcels: List[ProjectParcelCreate] = []

class ProjectStageTransition(BaseModel):
    target_stage: str
    reason: Optional[str] = None

class ProjectLifecycleResponse(BaseModel):
    project_id: str
    current_stage: str
    allowed_next_stages: List[str]
    stage_history: List[ProjectTimelineEventResponse] = []

class ProjectResponse(ProjectBase):
    project_id: str
    project_code: str
    current_stage: str
    created_at: datetime
    updated_at: datetime
    data_origin: str
    parcels: List[ProjectParcelResponse] = []
    timeline_events: List[ProjectTimelineEventResponse] = []

    class Config:
        from_attributes = True
