from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectResponse, ProjectParcelCreate,
    ProjectParcelResponse, ProjectTimelineEventResponse,
    ProjectStageTransition, ProjectLifecycleResponse
)
from app.services import project_service

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingest a new land acquisition project and create canonical representation.
    """
    return project_service.create_project(db=db, project_in=project_in, actor_id=current_user.id)

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    project_type: Optional[str] = Query(None),
    project_sector: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    taluka: Optional[str] = Query(None),
    project_status: Optional[str] = Query(None),
    acquisition_stage: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List and filter land acquisition projects with pagination.
    """
    return project_service.list_projects(
        db=db,
        project_type=project_type,
        project_sector=project_sector,
        state=state,
        district=district,
        taluka=taluka,
        project_status=project_status,
        acquisition_stage=acquisition_stage,
        skip=skip,
        limit=limit
    )

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve project identity, jurisdiction, stage, parcels, and timeline details.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects/{project_id}/parcels", response_model=ProjectParcelResponse)
def add_parcel_to_project(
    project_id: str,
    parcel_in: ProjectParcelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Attach a new parcel to an existing project.
    """
    return project_service.add_parcel_to_project(db=db, project_id=project_id, parcel_in=parcel_in)

@router.get("/projects/{project_id}/parcels", response_model=List[ProjectParcelResponse])
def list_project_parcels(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all parcels associated with a project.
    """
    return project_service.list_project_parcels(db=db, project_id=project_id)

@router.get("/parcels/{parcel_id}", response_model=ProjectParcelResponse)
def get_parcel(
    parcel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve specific parcel details.
    """
    parcel = project_service.get_parcel(db=db, parcel_id=parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel

@router.get("/projects/{project_id}/timeline", response_model=List[ProjectTimelineEventResponse])
def get_project_timeline(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve full chronological event timeline for a project.
    """
    return project_service.get_project_timeline(db=db, project_id=project_id)

@router.get("/projects/{project_id}/lifecycle", response_model=ProjectLifecycleResponse)
def get_project_lifecycle(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve current acquisition stage, allowed next stages, and stage transition history.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_next = project_service.get_allowed_next_stages(project.current_stage)
    timeline = project_service.get_project_timeline(db=db, project_id=project_id)
    stage_events = [e for e in timeline if e.event_type in ["Project Created", "Stage Transitioned"]]

    return ProjectLifecycleResponse(
        project_id=project.project_id,
        current_stage=project.current_stage,
        allowed_next_stages=allowed_next,
        stage_history=stage_events
    )

@router.post("/projects/{project_id}/lifecycle/transition", response_model=ProjectResponse)
def transition_project_stage(
    project_id: str,
    transition_in: ProjectStageTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate and execute acquisition stage transition with audit logging.
    """
    return project_service.transition_project_stage(
        db=db, project_id=project_id, transition_in=transition_in, actor_id=current_user.id
    )
