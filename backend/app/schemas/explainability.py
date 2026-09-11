from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExplanationDriver(BaseModel):
    feature_name: str
    observed_value: float
    importance: float
    human_label: str
    supporting_evidence_type: Optional[str] = None
    supporting_source_id: Optional[str] = None

class UncertaintyItem(BaseModel):
    title: str
    description: str
    impact: str

class ExplanationResponse(BaseModel):
    explanation_id: str
    project_id: str
    prediction_id: Optional[str] = None
    explanation_version: str
    summary: str
    risk_level: str
    predicted_probability: float
    prediction_horizon_days: int
    top_drivers: List[ExplanationDriver]
    uncertainties: List[UncertaintyItem]
    created_at: Optional[datetime] = None
    data_origin: str

class InterventionResponse(BaseModel):
    intervention_id: str
    project_id: str
    bottleneck_id: Optional[str] = None
    title: str
    description: str
    target_bottleneck: str
    priority: str
    expected_process_effect: str
    required_evidence: Optional[str] = None
    rule_id: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True
