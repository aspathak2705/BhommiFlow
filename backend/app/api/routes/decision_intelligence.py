from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.decision_intelligence import (
    DecisionContextResponse, OfficerDecisionCreate, OfficerDecisionResponse,
    OfficerActionCreate, OfficerActionResponse, ActionOutcomeUpdate, DecisionAuditEventResponse
)
from app.services.decision_intelligence_service import DecisionIntelligenceService, OfficerWorkflowService

router = APIRouter()

@router.get("/projects/{project_id}/decision-context", response_model=DecisionContextResponse)
def get_decision_context(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve structured officer decision context including prediction, bottlenecks, interventions, required evidence, and grounding.
    """
    return DecisionIntelligenceService.get_decision_context(db=db, project_id=project_id)

@router.post("/projects/{project_id}/decisions", response_model=OfficerDecisionResponse)
def create_officer_decision(
    project_id: str,
    decision_in: OfficerDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record an officer decision on recommendations (ACCEPT, REJECT, DEFER, REQUEST_EVIDENCE, ESCALATE).
    """
    return OfficerWorkflowService.create_decision(db=db, project_id=project_id, decision_in=decision_in, officer_id=current_user.id)

@router.get("/projects/{project_id}/decisions", response_model=List[OfficerDecisionResponse])
def get_officer_decisions(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List historical officer decisions for the project.
    """
    return OfficerWorkflowService.get_decisions(db=db, project_id=project_id)

@router.post("/projects/{project_id}/actions", response_model=OfficerActionResponse)
def create_officer_action(
    project_id: str,
    action_in: OfficerActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record an administrative officer action initiated from a decision context.
    """
    return OfficerWorkflowService.create_action(db=db, project_id=project_id, action_in=action_in, officer_id=current_user.id)

@router.get("/projects/{project_id}/actions", response_model=List[OfficerActionResponse])
def get_officer_actions(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List administrative actions initiated for the project.
    """
    return OfficerWorkflowService.get_actions(db=db, project_id=project_id)

@router.patch("/projects/{project_id}/actions/{action_id}/outcome", response_model=OfficerActionResponse)
def update_action_outcome(
    project_id: str,
    action_id: str,
    outcome_in: ActionOutcomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record resolution outcome feedback for an officer action.
    """
    return OfficerWorkflowService.update_action_outcome(db=db, project_id=project_id, action_id=action_id, outcome_in=outcome_in, officer_id=current_user.id)

@router.get("/projects/{project_id}/audit", response_model=List[DecisionAuditEventResponse])
def get_decision_audit_trail(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve full auditable lifecycle events for the project.
    """
    return OfficerWorkflowService.get_audit_trail(db=db, project_id=project_id)
