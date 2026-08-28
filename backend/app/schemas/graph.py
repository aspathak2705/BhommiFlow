from pydantic import BaseModel
from typing import List, Dict, Any

class GraphNode(BaseModel):
    id: str
    type: str  # CASE, PERSON, LAND_PARCEL, DOCUMENT, EVIDENCE, EVENT
    label: str
    details: Dict[str, Any]

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # INVOLVES, ASSOCIATED_WITH, MENTIONED_IN, RELATES_TO, ATTACHED_TO, SUPPORTED_BY, GENERATED, FOLLOWED_BY, COMPARES_WITH

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
