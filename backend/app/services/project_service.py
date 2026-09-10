import uuid
import random
import string
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.models.project import (
    Project, ProjectParcel, ProjectTimelineEvent,
    AcquisitionStage, ProjectStatus, ParcelStatus,
    ActorType, DataOrigin, ProjectType, ProjectScale
)
from app.schemas.project import (
    ProjectCreate, ProjectParcelCreate, ProjectStageTransition
)

# Canonical stage transition ordering
LIFECYCLE_STAGE_ORDER = [
    AcquisitionStage.NOTIFICATION.value,
    AcquisitionStage.SIA.value,
    AcquisitionStage.OBJECTION_RESOLUTION.value,
    AcquisitionStage.APPROVAL.value,
    AcquisitionStage.COMPENSATION.value,
    AcquisitionStage.RR.value,
    AcquisitionStage.POSSESSION.value,
    AcquisitionStage.LEGAL_RESOLUTION.value,
    AcquisitionStage.COMPLETION_PREPARATION.value,
    AcquisitionStage.COMPLETED.value,
]

VALID_PROJECT_TYPES = [e.value for e in ProjectType]
VALID_PROJECT_SCALES = [e.value for e in ProjectScale]
VALID_PROJECT_STATUSES = [e.value for e in ProjectStatus]
VALID_PARCEL_STATUSES = [e.value for e in ParcelStatus]

def generate_project_code(db: Session) -> str:
    # Format: BS-PROJ-XXXXXX
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"BS-PROJ-{chars}"
    while db.query(Project).filter(Project.project_code == code).first() is not None:
        chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"BS-PROJ-{chars}"
    return code

def create_project(db: Session, project_in: ProjectCreate, actor_id: Optional[str] = None) -> Project:
    # Validate controlled vocabulary
    if project_in.project_type not in VALID_PROJECT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project_type '{project_in.project_type}'. Must be one of: {VALID_PROJECT_TYPES}"
        )
    if project_in.project_scale not in VALID_PROJECT_SCALES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project_scale '{project_in.project_scale}'. Must be one of: {VALID_PROJECT_SCALES}"
        )
    if project_in.project_status not in VALID_PROJECT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project_status '{project_in.project_status}'. Must be one of: {VALID_PROJECT_STATUSES}"
        )

    project_id = f"PROJ-{uuid.uuid4().hex[:12].upper()}"
    code = generate_project_code(db)

    db_project = Project(
        project_id=project_id,
        project_code=code,
        project_name=project_in.project_name,
        project_type=project_in.project_type,
        project_sector=project_in.project_sector,
        project_scale=project_in.project_scale,
        state=project_in.state,
        district=project_in.district,
        taluka=project_in.taluka,
        village=project_in.village,
        project_start_date=project_in.project_start_date,
        planned_completion_date=project_in.planned_completion_date,
        land_required_area=project_in.land_required_area,
        land_area_unit=project_in.land_area_unit,
        affected_families=project_in.affected_families,
        affected_landholders=project_in.affected_landholders,
        current_stage=AcquisitionStage.NOTIFICATION.value,
        project_status=project_in.project_status,
        description=project_in.description,
        data_origin=DataOrigin.SYNTHETIC.value,
    )
    db.add(db_project)

    # Attach initial parcels if provided
    for p in project_in.parcels:
        parcel_id = f"PARCEL-{uuid.uuid4().hex[:12].upper()}"
        db_parcel = ProjectParcel(
            parcel_id=parcel_id,
            project_id=project_id,
            survey_number=p.survey_number,
            subdivision_number=p.subdivision_number,
            state=p.state,
            district=p.district,
            taluka=p.taluka,
            village=p.village,
            land_type=p.land_type,
            area=p.area,
            area_unit=p.area_unit,
            parcel_status=p.parcel_status if p.parcel_status in VALID_PARCEL_STATUSES else ParcelStatus.IDENTIFIED.value,
            geometry=p.geometry,
            data_origin=DataOrigin.SYNTHETIC.value,
        )
        db.add(db_parcel)

    # Initialize Project Created timeline event
    init_event = ProjectTimelineEvent(
        event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        project_id=project_id,
        event_type="Project Created",
        stage=AcquisitionStage.NOTIFICATION.value,
        description=f"Project '{project_in.project_name}' created under code {code}.",
        actor_type=ActorType.OFFICER.value if actor_id else ActorType.SYSTEM.value,
        actor_id=actor_id,
        status="COMPLETED",
        metadata_json=json.dumps({"project_code": code, "initial_stage": AcquisitionStage.NOTIFICATION.value}),
        data_origin=DataOrigin.SYNTHETIC.value,
    )
    db.add(init_event)

    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: str) -> Optional[Project]:
    return db.query(Project).filter(Project.project_id == project_id).first()


def list_projects(
    db: Session,
    project_type: Optional[str] = None,
    project_sector: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    taluka: Optional[str] = None,
    project_status: Optional[str] = None,
    acquisition_stage: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Project]:
    query = db.query(Project)
    if project_type:
        query = query.filter(Project.project_type == project_type)
    if project_sector:
        query = query.filter(Project.project_sector == project_sector)
    if state:
        query = query.filter(Project.state == state)
    if district:
        query = query.filter(Project.district == district)
    if taluka:
        query = query.filter(Project.taluka == taluka)
    if project_status:
        query = query.filter(Project.project_status == project_status)
    if acquisition_stage:
        query = query.filter(Project.current_stage == acquisition_stage)

    return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def add_parcel_to_project(db: Session, project_id: str, parcel_in: ProjectParcelCreate) -> ProjectParcel:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if parcel_in.parcel_status not in VALID_PARCEL_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parcel_status '{parcel_in.parcel_status}'. Must be one of: {VALID_PARCEL_STATUSES}"
        )

    parcel_id = f"PARCEL-{uuid.uuid4().hex[:12].upper()}"
    db_parcel = ProjectParcel(
        parcel_id=parcel_id,
        project_id=project_id,
        survey_number=parcel_in.survey_number,
        subdivision_number=parcel_in.subdivision_number,
        state=parcel_in.state,
        district=parcel_in.district,
        taluka=parcel_in.taluka,
        village=parcel_in.village,
        land_type=parcel_in.land_type,
        area=parcel_in.area,
        area_unit=parcel_in.area_unit,
        parcel_status=parcel_in.parcel_status,
        geometry=parcel_in.geometry,
        data_origin=DataOrigin.SYNTHETIC.value,
    )
    db.add(db_parcel)

    event = ProjectTimelineEvent(
        event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        project_id=project_id,
        parcel_id=parcel_id,
        event_type="Parcel Added",
        stage=project.current_stage,
        description=f"Parcel (Survey No. {parcel_in.survey_number}) added to project.",
        actor_type=ActorType.SYSTEM.value,
        status="COMPLETED",
        data_origin=DataOrigin.SYNTHETIC.value,
    )
    db.add(event)

    db.commit()
    db.refresh(db_parcel)
    return db_parcel


def list_project_parcels(db: Session, project_id: str) -> List[ProjectParcel]:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(ProjectParcel).filter(ProjectParcel.project_id == project_id).all()


def get_parcel(db: Session, parcel_id: str) -> Optional[ProjectParcel]:
    return db.query(ProjectParcel).filter(ProjectParcel.parcel_id == parcel_id).first()


def get_allowed_next_stages(current_stage: str) -> List[str]:
    valid_stages = [e.value for e in AcquisitionStage]
    if current_stage not in valid_stages:
        return [AcquisitionStage.NOTIFICATION.value]
    
    idx = LIFECYCLE_STAGE_ORDER.index(current_stage) if current_stage in LIFECYCLE_STAGE_ORDER else -1
    if idx == -1 or idx >= len(LIFECYCLE_STAGE_ORDER) - 1:
        # Legal resolution can be transitioned to or back to primary flow
        return [AcquisitionStage.LEGAL_RESOLUTION.value, AcquisitionStage.COMPLETED.value]
    
    next_primary = LIFECYCLE_STAGE_ORDER[idx + 1]
    # Allow transitioning to next primary stage or parallel Legal Resolution
    stages = [next_primary]
    if current_stage != AcquisitionStage.LEGAL_RESOLUTION.value:
        stages.append(AcquisitionStage.LEGAL_RESOLUTION.value)
    return stages


def transition_project_stage(
    db: Session, project_id: str, transition_in: ProjectStageTransition, actor_id: Optional[str] = None
) -> Project:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_next = get_allowed_next_stages(project.current_stage)
    if transition_in.target_stage not in allowed_next and transition_in.target_stage not in LIFECYCLE_STAGE_ORDER:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid stage transition from '{project.current_stage}' to '{transition_in.target_stage}'. Allowed next stages: {allowed_next}"
        )

    previous_stage = project.current_stage
    project.current_stage = transition_in.target_stage

    event = ProjectTimelineEvent(
        event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        project_id=project_id,
        event_type="Stage Transitioned",
        stage=transition_in.target_stage,
        description=f"Lifecycle stage transitioned from '{previous_stage}' to '{transition_in.target_stage}'." + (f" Reason: {transition_in.reason}" if transition_in.reason else ""),
        actor_type=ActorType.OFFICER.value if actor_id else ActorType.SYSTEM.value,
        actor_id=actor_id,
        status="COMPLETED",
        metadata_json=json.dumps({"previous_stage": previous_stage, "new_stage": transition_in.target_stage, "reason": transition_in.reason}),
        data_origin=DataOrigin.SYNTHETIC.value,
    )
    db.add(event)

    db.commit()
    db.refresh(project)
    return project


def get_project_timeline(db: Session, project_id: str) -> List[ProjectTimelineEvent]:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(ProjectTimelineEvent).filter(ProjectTimelineEvent.project_id == project_id).order_by(ProjectTimelineEvent.event_date.asc()).all()
