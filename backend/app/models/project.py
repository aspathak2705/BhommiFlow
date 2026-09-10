from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Enum as SQLEnum, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectType(str, Enum):
    HIGHWAY = "Highway"
    RAILWAY = "Railway"
    METRO = "Metro"
    INDUSTRIAL_CORRIDOR = "Industrial Corridor"
    IRRIGATION = "Irrigation"
    POWER_TRANSMISSION = "Power Transmission"
    AIRPORT_EXPANSION = "Airport Expansion"
    URBAN_INFRASTRUCTURE = "Urban Infrastructure"
    WATER_SUPPLY = "Water Supply"
    PUBLIC_UTILITY = "Public Utility"
    OTHER = "Other"

class ProjectScale(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    VERY_LARGE = "Very Large"

class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class AcquisitionStage(str, Enum):
    NOTIFICATION = "Notification"
    SIA = "SIA"
    OBJECTION_RESOLUTION = "Objection Resolution"
    APPROVAL = "Approval"
    COMPENSATION = "Compensation"
    RR = "R&R"
    POSSESSION = "Possession"
    LEGAL_RESOLUTION = "Legal Resolution"
    COMPLETION_PREPARATION = "Completion Preparation"
    COMPLETED = "Completed"

class ParcelStatus(str, Enum):
    IDENTIFIED = "Identified"
    UNDER_VERIFICATION = "Under Verification"
    UNDER_ACQUISITION = "Under Acquisition"
    COMPENSATION_PENDING = "Compensation Pending"
    POSSESSION_PENDING = "Possession Pending"
    POSSESSED = "Possessed"
    DISPUTED = "Disputed"
    EXCLUDED = "Excluded"
    COMPLETED = "Completed"

class ActorType(str, Enum):
    CITIZEN = "Citizen"
    OFFICER = "Officer"
    SYSTEM = "System"
    EXTERNAL_AGENCY = "External Agency"

class DataOrigin(str, Enum):
    SYNTHETIC = "synthetic"
    USER_SUBMITTED = "user_submitted"
    GOVERNMENT_SOURCE = "government_source"
    SYSTEM_GENERATED = "system_generated"
    IMPORTED = "imported"

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, index=True)
    project_code = Column(String, unique=True, index=True, nullable=False)
    project_name = Column(String, nullable=False, index=True)
    project_type = Column(String, nullable=False, index=True)
    project_sector = Column(String, nullable=True, index=True)
    project_scale = Column(String, nullable=False, default=ProjectScale.MEDIUM.value)

    state = Column(String, nullable=False, index=True)
    district = Column(String, nullable=False, index=True)
    taluka = Column(String, nullable=False, index=True)
    village = Column(String, nullable=False)

    project_start_date = Column(DateTime(timezone=True), nullable=False)
    planned_completion_date = Column(DateTime(timezone=True), nullable=False)

    land_required_area = Column(Float, nullable=False)
    land_area_unit = Column(String, nullable=False, default="Hectares")

    affected_families = Column(Integer, nullable=False, default=0)
    affected_landholders = Column(Integer, nullable=False, default=0)

    current_stage = Column(String, nullable=False, default=AcquisitionStage.NOTIFICATION.value, index=True)
    project_status = Column(String, nullable=False, default=ProjectStatus.DRAFT.value, index=True)

    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    data_origin = Column(String, nullable=False, default=DataOrigin.SYNTHETIC.value)

    parcels = relationship("ProjectParcel", back_populates="project", cascade="all, delete-orphan")
    timeline_events = relationship("ProjectTimelineEvent", back_populates="project", cascade="all, delete-orphan")


class ProjectParcel(Base):
    __tablename__ = "project_parcels"

    parcel_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)

    survey_number = Column(String, nullable=False, index=True)
    subdivision_number = Column(String, nullable=True)

    state = Column(String, nullable=False, index=True)
    district = Column(String, nullable=False, index=True)
    taluka = Column(String, nullable=False, index=True)
    village = Column(String, nullable=False)

    land_type = Column(String, nullable=False, default="Agricultural")

    area = Column(Float, nullable=False)
    area_unit = Column(String, nullable=False, default="Hectares")

    parcel_status = Column(String, nullable=False, default=ParcelStatus.IDENTIFIED.value, index=True)

    # Geometry string (WKT, GeoJSON, or PostGIS geometry)
    geometry = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    data_origin = Column(String, nullable=False, default=DataOrigin.SYNTHETIC.value)

    project = relationship("Project", back_populates="parcels")
    timeline_events = relationship("ProjectTimelineEvent", back_populates="parcel")


class ProjectTimelineEvent(Base):
    __tablename__ = "project_timeline_events"

    event_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    parcel_id = Column(String, ForeignKey("project_parcels.parcel_id", ondelete="SET NULL"), nullable=True, index=True)

    event_type = Column(String, nullable=False, index=True)
    event_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    stage = Column(String, nullable=True)
    description = Column(Text, nullable=False)

    actor_type = Column(String, nullable=False, default=ActorType.SYSTEM.value)
    actor_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    status = Column(String, nullable=False, default="COMPLETED")
    metadata_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default=DataOrigin.SYNTHETIC.value)

    project = relationship("Project", back_populates="timeline_events")
    parcel = relationship("ProjectParcel", back_populates="timeline_events")
    actor = relationship("User")
