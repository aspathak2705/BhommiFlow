from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FeatureVectorResponse(BaseModel):
    project_id: str
    feature_schema_version: str
    features: Dict[str, float]

class PredictionResponse(BaseModel):
    prediction_id: str
    project_id: str
    model_version: str
    feature_schema_version: str
    predicted_probability: float
    risk_level: str
    horizon_days: int
    top_contributing_features: List[Dict[str, Any]]
    created_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True
