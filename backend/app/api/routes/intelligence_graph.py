from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.intelligence_graph import (
    ProjectGraphResponse, ProcessDependencyResponse,
    BottleneckResponse, DelayPropagationResponse, TimelineIntelligenceResponse
)
from app.services.intelligence_graph_service import (
    GraphBuilderService, ProcessDependencyService,
    BottleneckEngineService, DelayPropagationEngine, TimelineIntelligenceService
)

router = APIRouter()

@router.get("/projects/{project_id}/graph", response_model=ProjectGraphResponse)
def get_project_graph(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve connected entity and evidence graph for a project.
    """
    return GraphBuilderService.build_project_graph(db=db, project_id=project_id)

@router.get("/projects/{project_id}/dependencies", response_model=List[ProcessDependencyResponse])
def get_project_dependencies(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve process dependency graph for a project.
    """
    return ProcessDependencyService.get_dependencies(db=db, project_id=project_id)

@router.get("/projects/{project_id}/bottlenecks", response_model=BottleneckResponse)
def get_project_bottlenecks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate and retrieve current primary/secondary project bottlenecks.
    """
    return BottleneckEngineService.evaluate_bottlenecks(db=db, project_id=project_id)

@router.get("/projects/{project_id}/propagation", response_model=DelayPropagationResponse)
def get_project_delay_propagation(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate and retrieve downstream delay propagation and critical path impacts.
    """
    return DelayPropagationEngine.calculate_propagation(db=db, project_id=project_id)

@router.get("/projects/{project_id}/timeline/intelligence", response_model=TimelineIntelligenceResponse)
def get_project_timeline_intelligence(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve deterministic timeline signals and duration intelligence.
    """
    return TimelineIntelligenceService.get_timeline_intelligence(db=db, project_id=project_id)
