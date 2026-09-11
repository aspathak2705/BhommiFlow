import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project, ProjectParcel, ProjectTimelineEvent
from app.models.evidence_intelligence import BhoomiDocument, EvidenceRecord, CrossRecordComparison, ConflictSignal
from app.models.intelligence_graph import ProcessDependency, BottleneckSignal, DelayPropagation
from app.schemas.intelligence_graph import (
    GraphNode, GraphEdge, ProjectGraphResponse,
    ProcessDependencyResponse, BottleneckResponse,
    DelayPropagationResponse, TimelineIntelligenceResponse
)

# Canonical acquisition process dependencies
CANONICAL_DEPENDENCIES = [
    ("Ownership Verification", "Compensation", "DEPENDS_ON", "RULE-DEP-01"),
    ("Survey Verification", "Compensation", "DEPENDS_ON", "RULE-DEP-02"),
    ("Approval", "Compensation", "DEPENDS_ON", "RULE-DEP-03"),
    ("Compensation", "Possession", "DEPENDS_ON", "RULE-DEP-04"),
    ("R&R", "Possession", "DEPENDS_ON", "RULE-DEP-05"),
    ("Legal Resolution", "Compensation", "DEPENDS_ON", "RULE-DEP-06"),
    ("Legal Resolution", "Possession", "DEPENDS_ON", "RULE-DEP-07"),
    ("Possession", "Completion Preparation", "DEPENDS_ON", "RULE-DEP-08")
]

class GraphBuilderService:
    @staticmethod
    def build_project_graph(db: Session, project_id: str) -> ProjectGraphResponse:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # 1. Project Root Node
        nodes.append(GraphNode(
            id=project.project_id,
            node_type="Project",
            label=project.project_name,
            metadata={"code": project.project_code, "stage": project.current_stage, "type": project.project_type}
        ))

        # 2. Parcels
        parcels = db.query(ProjectParcel).filter(ProjectParcel.project_id == project_id).all()
        for p in parcels:
            nodes.append(GraphNode(
                id=p.parcel_id,
                node_type="Parcel",
                label=f"Survey {p.survey_number}",
                metadata={"village": p.village, "area": p.area, "status": p.parcel_status}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source=project.project_id,
                target=p.parcel_id,
                relationship_type="PROJECT_CONTAINS_PARCEL",
                reason=f"Parcel {p.survey_number} is part of project area."
            ))

        # 3. Documents
        documents = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id).all()
        for doc in documents:
            nodes.append(GraphNode(
                id=doc.document_id,
                node_type="Document",
                label=doc.file_name,
                metadata={"type": doc.document_type, "status": doc.extraction_status, "origin": doc.data_origin}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source=project.project_id,
                target=doc.document_id,
                relationship_type="PROJECT_HAS_DOCUMENT",
                reason=f"Document uploaded for project {project.project_code}."
            ))
            if doc.parcel_id:
                edges.append(GraphEdge(
                    id=f"EDGE-{uuid.uuid4().hex[:8]}",
                    source=doc.document_id,
                    target=doc.parcel_id,
                    relationship_type="DOCUMENT_REFERENCES_PARCEL",
                    reason=f"Document explicitly references parcel {doc.parcel_id}."
                ))

        # 4. Evidence Records
        evidence_items = db.query(EvidenceRecord).filter(EvidenceRecord.project_id == project_id).all()
        for ev in evidence_items:
            nodes.append(GraphNode(
                id=ev.evidence_id,
                node_type="Evidence",
                label=f"{ev.evidence_type}: {ev.normalized_value or ev.raw_value}",
                metadata={"field": ev.field_name, "confidence": ev.confidence, "status": ev.verification_status}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source=ev.document_id,
                target=ev.evidence_id,
                relationship_type="DOCUMENT_CONTAINS_EVIDENCE",
                reason="Extracted fact sourced from document page."
            ))

        # 5. Conflicts
        conflicts = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id).all()
        for cnf in conflicts:
            nodes.append(GraphNode(
                id=cnf.conflict_id,
                node_type="Conflict",
                label=cnf.title,
                metadata={"severity": cnf.severity, "status": cnf.status}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-{uuid.uuid4().hex[:8]}",
                source=project.project_id,
                target=cnf.conflict_id,
                relationship_type="PROJECT_HAS_CONFLICT",
                reason="Discrepancy signal generated from cross-record evaluation."
            ))

        return ProjectGraphResponse(project_id=project_id, nodes=nodes, edges=edges)


class ProcessDependencyService:
    @staticmethod
    def get_dependencies(db: Session, project_id: str) -> List[ProcessDependencyResponse]:
        # Return canonical dependency rules plus any project specific custom overrides
        res = []
        for src, tgt, dep_type, rule in CANONICAL_DEPENDENCIES:
            res.append(ProcessDependencyResponse(
                dependency_id=f"DEP-{rule}",
                project_id=project_id,
                source_process=src,
                target_process=tgt,
                dependency_type=dep_type,
                active=True,
                rule_id=rule
            ))
        return res


class BottleneckEngineService:
    @staticmethod
    def evaluate_bottlenecks(db: Session, project_id: str) -> BottleneckResponse:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        conflicts = db.query(ConflictSignal).filter(
            ConflictSignal.project_id == project_id,
            ConflictSignal.status == "Open"
        ).all()
        documents = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id).all()
        timeline = db.query(ProjectTimelineEvent).filter(ProjectTimelineEvent.project_id == project_id).order_by(ProjectTimelineEvent.event_date.desc()).all()

        supporting_signals = []
        primary_bottleneck = "None"
        secondary_bottleneck = None
        severity = "Low"
        age_days = 0

        # Calculate stage age
        if project.created_at:
            now = datetime.now(timezone.utc)
            created = project.created_at if project.created_at.tzinfo else project.created_at.replace(tzinfo=timezone.utc)
            age_days = (now - created).days

        # Rule 1: High severity conflicts or document discrepancies -> Ownership Verification
        high_conflicts = [c for c in conflicts if c.severity in ["High", "Critical"]]
        if len(high_conflicts) > 0:
            primary_bottleneck = "Ownership Verification"
            severity = "High"
            supporting_signals.append(f"{len(high_conflicts)} high-severity document conflict signal(s) active.")
            supporting_signals.append("Survey & owner name variations require human verification.")
        
        # Rule 2: Unextracted or pending documents -> Documentation
        pending_docs = [d for d in documents if d.extraction_status in ["Pending", "Needs Review"]]
        if len(pending_docs) > 0:
            if primary_bottleneck == "None":
                primary_bottleneck = "Documentation"
                severity = "Medium"
            else:
                secondary_bottleneck = "Documentation"
            supporting_signals.append(f"{len(pending_docs)} document(s) pending extraction/review.")

        # Rule 3: Legal resolution stage
        if project.current_stage == "Legal Resolution":
            primary_bottleneck = "Legal Resolution"
            severity = "Critical"
            supporting_signals.append("Project lifecycle explicitly held in Legal Resolution stage.")

        # Fallback for draft projects without blockers
        if primary_bottleneck == "None" and project.current_stage == "Notification":
            primary_bottleneck = "Notification"
            severity = "Low"
            supporting_signals.append("Initial notification stage in progress.")

        db_signal = BottleneckSignal(
            bottleneck_id=f"BTN-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            primary_bottleneck=primary_bottleneck,
            secondary_bottleneck=secondary_bottleneck,
            severity=severity,
            age_days=age_days,
            supporting_signals_json=json.dumps(supporting_signals),
            rule_id="RULE-BTN-ENGINE-V1",
            data_origin="synthetic"
        )
        db.add(db_signal)
        db.commit()

        return BottleneckResponse(
            bottleneck_id=db_signal.bottleneck_id,
            project_id=project_id,
            primary_bottleneck=primary_bottleneck,
            secondary_bottleneck=secondary_bottleneck,
            severity=severity,
            age_days=age_days,
            supporting_signals=supporting_signals,
            rule_id="RULE-BTN-ENGINE-V1",
            generated_at=db_signal.generated_at
        )


class DelayPropagationEngine:
    @staticmethod
    def calculate_propagation(db: Session, project_id: str) -> DelayPropagationResponse:
        btn = BottleneckEngineService.evaluate_bottlenecks(db, project_id)
        blocker = btn.primary_bottleneck

        chain = [blocker]
        affected = []
        critical_path = False

        if blocker in ["Ownership Verification", "Survey Verification"]:
            chain.extend(["Compensation", "Possession", "Completion Preparation"])
            affected = ["Compensation", "Possession", "Completion Preparation"]
            critical_path = True
        elif blocker == "Compensation":
            chain.extend(["Possession", "Completion Preparation"])
            affected = ["Possession", "Completion Preparation"]
            critical_path = True
        elif blocker == "Legal Resolution":
            chain.extend(["Compensation", "Possession", "Completion Preparation"])
            affected = ["Compensation", "Possession", "Completion Preparation"]
            critical_path = True
        else:
            affected = []

        db_prop = DelayPropagation(
            propagation_id=f"PRP-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            root_blocker=blocker,
            dependency_chain_json=json.dumps(chain),
            affected_processes_json=json.dumps(affected),
            propagation_depth=len(chain) - 1,
            critical_path_affected=critical_path,
            data_origin="synthetic"
        )
        db.add(db_prop)
        db.commit()

        return DelayPropagationResponse(
            propagation_id=db_prop.propagation_id,
            project_id=project_id,
            root_blocker=blocker,
            dependency_chain=chain,
            affected_processes=affected,
            propagation_depth=len(chain) - 1,
            critical_path_affected=critical_path,
            generated_at=db_prop.generated_at
        )


class TimelineIntelligenceService:
    @staticmethod
    def get_timeline_intelligence(db: Session, project_id: str) -> TimelineIntelligenceResponse:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        now = datetime.now(timezone.utc)
        created = project.created_at if project.created_at.tzinfo else project.created_at.replace(tzinfo=timezone.utc)
        duration_days = (now - created).days

        unresolved = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id, ConflictSignal.status == "Open").count()
        pending_docs = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id, BhoomiDocument.extraction_status != "Completed").count()
        inactivity = duration_days > 30 and unresolved > 0

        summary = f"Project '{project.project_name}' has been in stage '{project.current_stage}' for {duration_days} day(s)."
        if unresolved > 0:
            summary += f" Currently blocked by {unresolved} unresolved document conflict signal(s)."

        return TimelineIntelligenceResponse(
            project_id=project_id,
            current_stage=project.current_stage,
            stage_duration_days=duration_days,
            unresolved_conflicts_count=unresolved,
            pending_documents_count=pending_docs,
            inactivity_signal=inactivity,
            intelligence_summary=summary
        )
