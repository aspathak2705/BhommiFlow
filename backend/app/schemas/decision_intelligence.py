from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RequiredEvidenceItem(BaseModel):
    document_type: str
    title: str
    status: str  # MISSING, AVAILABLE, UNDER_REVIEW, VERIFIED
    source_reference: Optional[str] = None

class DecisionContextResponse(BaseModel):
    project_id: str
    decision_priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    risk_level: str
    predicted_probability: float
    horizon_days: int
    summary: str
    top_drivers: List[Dict[str, Any]]
    primary_bottleneck: Optional[str] = None
    bottleneck_severity: Optional[str] = None
    interventions: List[Dict[str, Any]]
    required_evidence: List[RequiredEvidenceItem]
    uncertainties: List[Dict[str, Any]]
    procedure_grounding: Optional[Dict[str, Any]] = None
    pending_decisions: List[Dict[str, Any]] = []

class OfficerDecisionCreate(BaseModel):
    prediction_id: Optional[str] = None
    intervention_id: Optional[str] = None
    decision_type: str # REVIEW, ACCEPT_RECOMMENDATION, REJECT_RECOMMENDATION, DEFER, REQUEST_EVIDENCE, ESCALATE, MARK_RESOLVED
    decision_reason: Optional[str] = None
    selected_action: Optional[str] = None

class OfficerDecisionResponse(BaseModel):
    decision_id: str
    project_id: str
    prediction_id: Optional[str] = None
    intervention_id: Optional[str] = None
    officer_id: Optional[str] = None
    decision_type: str
    decision_status: str
    decision_reason: Optional[str] = None
    selected_action: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True

class OfficerActionCreate(BaseModel):
    decision_id: Optional[str] = None
    action_type: str # REQUEST_DOCUMENT, REQUEST_CLARIFICATION, VERIFY_RECORD, ESCALATE_CASE, FOLLOW_UP_STAKEHOLDER, REVIEW_CONFLICT, REVIEW_COMPENSATION, REVIEW_RR_STATUS, REVIEW_POSSESSION
    description: str
    target_entity: Optional[str] = None

class OfficerActionResponse(BaseModel):
    action_id: str
    project_id: str
    decision_id: Optional[str] = None
    officer_id: Optional[str] = None
    action_type: str
    description: str
    target_entity: Optional[str] = None
    status: str
    outcome_status: Optional[str] = None
    outcome_note: Optional[str] = None
    created_at: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True

class ActionOutcomeUpdate(BaseModel):
    outcome_status: str # RESOLVED, PARTIALLY_RESOLVED, NOT_RESOLVED, NO_ACTION_REQUIRED, DEFERRED
    outcome_note: Optional[str] = None

class DecisionAuditEventResponse(BaseModel):
    event_id: str
    project_id: str
    actor_id: str
    actor_type: str
    event_type: str
    target_entity: Optional[str] = None
    event_metadata_json: Optional[str] = None
    timestamp: Optional[datetime] = None
    data_origin: str

    class Config:
        from_attributes = True
