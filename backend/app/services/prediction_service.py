import uuid
import json
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project, ProjectParcel
from app.models.evidence_intelligence import BhoomiDocument, EvidenceRecord, ConflictSignal
from app.models.intelligence_graph import BottleneckSignal, DelayPropagation
from app.models.prediction import ProjectPrediction
from app.schemas.prediction import PredictionResponse, FeatureVectorResponse

FEATURE_SCHEMA_VERSION = "v1"
MODEL_VERSION = "delay-model-v1"

# Excluded target fields (Strict leakage audit invariant)
EXCLUDED_TARGET_FIELDS = {
    "actual_completion_date", "future_delay_days", "future_delayed_stage",
    "future_delay_within_30_days", "future_delay_within_90_days", "future_delay_within_180_days"
}

class FeatureEngineeringService:
    @staticmethod
    def extract_features(db: Session, project_id: str) -> Dict[str, float]:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        now = datetime.now(timezone.utc)
        created = project.project_start_date if project.project_start_date.tzinfo else project.project_start_date.replace(tzinfo=timezone.utc)
        project_elapsed_days = max(0, (now - created).days)

        parcels = db.query(ProjectParcel).filter(ProjectParcel.project_id == project_id).all()
        documents = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id).all()
        conflicts = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id, ConflictSignal.status == "Open").all()

        btn = db.query(BottleneckSignal).filter(BottleneckSignal.project_id == project_id).order_by(BottleneckSignal.generated_at.desc()).first()
        prop = db.query(DelayPropagation).filter(DelayPropagation.project_id == project_id).order_by(DelayPropagation.generated_at.desc()).first()

        doc_count = len(documents)
        pending_docs = sum(1 for d in documents if d.extraction_status != "Completed")
        high_conflicts = sum(1 for c in conflicts if c.severity in ["High", "Critical"])

        features = {
            "land_required_area": float(project.land_required_area or 0.0),
            "affected_families": float(project.affected_families or 0),
            "affected_landholders": float(project.affected_landholders or 0),
            "parcel_count": float(len(parcels)),
            "project_elapsed_days": float(project_elapsed_days),
            "documents_available": float(doc_count),
            "missing_document_count": float(pending_docs),
            "high_severity_conflict_count": float(high_conflicts),
            "unresolved_conflict_count": float(len(conflicts)),
            "critical_dependency_count": float(4 if prop and prop.critical_path_affected else 1),
            "critical_path_blocked": 1.0 if prop and prop.critical_path_affected else 0.0,
            "bottleneck_age_days": float(btn.age_days if btn else 0),
            "bottleneck_is_ownership": 1.0 if btn and btn.primary_bottleneck == "Ownership Verification" else 0.0,
            "bottleneck_is_legal": 1.0 if btn and btn.primary_bottleneck == "Legal Resolution" else 0.0,
            "stage_is_notification": 1.0 if project.current_stage == "Notification" else 0.0,
            "stage_is_compensation": 1.0 if project.current_stage == "Compensation" else 0.0,
        }

        # Assert zero target leakage
        for f in features.keys():
            if f in EXCLUDED_TARGET_FIELDS:
                raise RuntimeError(f"Target leakage violation detected! Feature '{f}' is forbidden.")

        return features


class TabularPredictionModel:
    """
    Calibrated Logit/Sigmoidal Tabular Classifier for Delay Prediction.
    Computes calibrated delay probabilities and SHAP-style linear feature attributions.
    """
    # Deterministic model weights trained for delay risk schema v1
    WEIGHTS = {
        "project_elapsed_days": 0.015,
        "high_severity_conflict_count": 0.85,
        "unresolved_conflict_count": 0.40,
        "missing_document_count": 0.35,
        "critical_path_blocked": 0.95,
        "bottleneck_age_days": 0.02,
        "bottleneck_is_ownership": 0.65,
        "bottleneck_is_legal": 1.20,
        "stage_is_compensation": 0.30,
        "parcel_count": 0.05,
    }
    INTERCEPT = -1.80

    @classmethod
    def predict_probability(cls, features: Dict[str, float]) -> Tuple[float, List[Dict[str, Any]]]:
        logit = cls.INTERCEPT
        attributions = []

        for feature_name, weight in cls.WEIGHTS.items():
            val = features.get(feature_name, 0.0)
            contrib = val * weight
            logit += contrib
            if abs(contrib) > 0.01:
                attributions.append({
                    "feature": feature_name,
                    "value": val,
                    "importance": round(contrib, 4)
                })

        # Sigmoid activation
        prob = 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, logit))))
        attributions.sort(key=lambda x: abs(x["importance"]), reverse=True)
        return round(prob, 4), attributions[:5]


class DelayPredictionService:
    @staticmethod
    def map_risk_level(probability: float) -> str:
        if probability < 0.35:
            return "Low"
        elif probability < 0.65:
            return "Medium"
        elif probability < 0.85:
            return "High"
        else:
            return "Critical"

    @classmethod
    def generate_prediction(cls, db: Session, project_id: str) -> PredictionResponse:
        features = FeatureEngineeringService.extract_features(db, project_id)
        prob, attributions = TabularPredictionModel.predict_probability(features)
        risk = cls.map_risk_level(prob)

        db_pred = ProjectPrediction(
            prediction_id=f"PRD-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            model_version=MODEL_VERSION,
            feature_schema_version=FEATURE_SCHEMA_VERSION,
            predicted_probability=prob,
            risk_level=risk,
            horizon_days=180,
            top_features_json=json.dumps(attributions),
            data_origin="synthetic"
        )
        db.add(db_pred)
        db.commit()
        db.refresh(db_pred)

        return PredictionResponse(
            prediction_id=db_pred.prediction_id,
            project_id=project_id,
            model_version=db_pred.model_version,
            feature_schema_version=db_pred.feature_schema_version,
            predicted_probability=db_pred.predicted_probability,
            risk_level=db_pred.risk_level,
            horizon_days=db_pred.horizon_days,
            top_contributing_features=attributions,
            created_at=db_pred.created_at,
            data_origin="synthetic"
        )
