from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GraphNode(BaseModel):
    id: str
    node_type: str  # Project, Parcel, Document, Evidence, Conflict, Event
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str  # PROJECT_CONTAINS_PARCEL, DOCUMENT_CONFLICTS_WITH_DOCUMENT, etc.
    reason: str

class ProjectGraphResponse(BaseModel):
    project_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ProcessDependencyResponse(BaseModel):
    dependency_id: str
    project_id: Optional[str] = None
    source_process: str
    target_process: str
    dependency_type: str
    active: bool
    rule_id: Optional[str] = None

class BottleneckResponse(BaseModel):
    bottleneck_id: str
    project_id: str
    primary_bottleneck: str
    secondary_bottleneck: Optional[str] = None
    severity: str
    age_days: int
    supporting_signals: List[str]
    rule_id: Optional[str] = None
    generated_at: Optional[datetime] = None

class DelayPropagationResponse(BaseModel):
    propagation_id: str
    project_id: str
    root_blocker: str
    dependency_chain: List[str]
    affected_processes: List[str]
    propagation_depth: int
    critical_path_affected: bool
    generated_at: Optional[datetime] = None

class TimelineIntelligenceResponse(BaseModel):
    project_id: str
    current_stage: str
    stage_duration_days: int
    unresolved_conflicts_count: int
    pending_documents_count: int
    inactivity_signal: bool
    intelligence_summary: str
