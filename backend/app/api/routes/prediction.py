from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.prediction import PredictionResponse, FeatureVectorResponse
from app.services.prediction_service import DelayPredictionService, FeatureEngineeringService
from app.models.prediction import ProjectPrediction
import json

router = APIRouter()

@router.post("/projects/{project_id}/prediction", response_model=PredictionResponse)
def create_project_prediction(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and persist ML delay risk prediction for a project.
    """
    return DelayPredictionService.generate_prediction(db=db, project_id=project_id)

@router.get("/projects/{project_id}/prediction", response_model=PredictionResponse)
def get_latest_project_prediction(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve latest delay risk prediction and top contributing features.
    """
    pred = db.query(ProjectPrediction).filter(ProjectPrediction.project_id == project_id).order_by(ProjectPrediction.created_at.desc()).first()
    if not pred:
        # Generate on the fly if not evaluated yet
        return DelayPredictionService.generate_prediction(db=db, project_id=project_id)

    top_features = json.loads(pred.top_features_json) if pred.top_features_json else []
    return PredictionResponse(
        prediction_id=pred.prediction_id,
        project_id=pred.project_id,
        model_version=pred.model_version,
        feature_schema_version=pred.feature_schema_version,
        predicted_probability=pred.predicted_probability,
        risk_level=pred.risk_level,
        horizon_days=pred.horizon_days,
        top_contributing_features=top_features,
        created_at=pred.created_at,
        data_origin=pred.data_origin
    )

@router.get("/projects/{project_id}/features", response_model=FeatureVectorResponse)
def get_project_feature_vector(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inspect raw deterministic feature vector generated for ML model input.
    """
    features = FeatureEngineeringService.extract_features(db=db, project_id=project_id)
    return FeatureVectorResponse(
        project_id=project_id,
        feature_schema_version="v1",
        features=features
    )
