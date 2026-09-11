from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.explainability import ExplanationResponse, InterventionResponse
from app.services.explainability_service import ExplainabilityService, InterventionService

router = APIRouter()

@router.get("/projects/{project_id}/explanation", response_model=ExplanationResponse)
def get_project_explanation(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve grounded explanation for ML delay risk prediction with evidence drivers & uncertainties.
    """
    return ExplainabilityService.generate_explanation(db=db, project_id=project_id)

@router.get("/projects/{project_id}/interventions", response_model=List[InterventionResponse])
def get_project_interventions(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve ranked intervention candidate recommendations for human officer review.
    """
    return InterventionService.generate_interventions(db=db, project_id=project_id)
