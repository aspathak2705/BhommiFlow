import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.evidence_intelligence import BhoomiDocument, ConflictSignal, EvidenceRecord
from app.models.intelligence_graph import BottleneckSignal, DelayPropagation
from app.models.prediction import ProjectPrediction
from app.models.explainability import ProjectExplanation, InterventionCandidate
from app.models.decision_intelligence import OfficerDecision, OfficerAction, DecisionAuditEvent
from app.schemas.decision_intelligence import (
    DecisionContextResponse, RequiredEvidenceItem, OfficerDecisionCreate,
    OfficerDecisionResponse, OfficerActionCreate, OfficerActionResponse,
    ActionOutcomeUpdate, DecisionAuditEventResponse
)
from app.services.prediction_service import DelayPredictionService
from app.services.explainability_service import ExplainabilityService, InterventionService

# Valid state transitions matrix
VALID_DECISION_TRANSITIONS = {
    "RECOMMENDED": ["REVIEWED", "ACCEPTED", "REJECTED", "DEFERRED"],
    "REVIEWED": ["ACCEPTED", "REJECTED", "DEFERRED", "ACTION_INITIATED"],
    "ACCEPTED": ["ACTION_INITIATED", "DEFERRED"],
    "REJECTED": [],
    "DEFERRED": ["REVIEWED", "ACCEPTED", "REJECTED"],
    "ACTION_INITIATED": ["AWAITING_OUTCOME", "RESOLVED"],
    "AWAITING_OUTCOME": ["RESOLVED", "DEFERRED"],
    "RESOLVED": []
}

class DecisionIntelligenceService:
    @staticmethod
    def get_decision_context(db: Session, project_id: str) -> DecisionContextResponse:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        exp = ExplainabilityService.generate_explanation(db, project_id)
        interventions_res = InterventionService.generate_interventions(db, project_id)
        btn = db.query(BottleneckSignal).filter(BottleneckSignal.project_id == project_id).order_by(BottleneckSignal.generated_at.desc()).first()

        # Deterministic Decision Priority Calculation
        priority = "LOW"
        if exp.risk_level == "Critical" or (btn and btn.severity == "High"):
            priority = "CRITICAL"
        elif exp.risk_level == "High":
            priority = "HIGH"
        elif exp.risk_level == "Medium":
            priority = "MEDIUM"

        # Evidence Status & Provenance Checklist (Available vs Verified)
        docs = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id).all()
        evidence_items: List[RequiredEvidenceItem] = []

        has_712 = any(d.document_type == "7/12 Extract" for d in docs)
        has_deed = any(d.document_type == "Sale Deed" for d in docs)

        # 7/12 Extract
        e_712_status = "MISSING"
        if has_712:
            ver_count = db.query(EvidenceRecord).filter(
                EvidenceRecord.project_id == project_id,
                EvidenceRecord.verification_status == "Verified"
            ).count()
            e_712_status = "VERIFIED" if ver_count > 0 else "AVAILABLE"

        evidence_items.append(RequiredEvidenceItem(
            document_type="7/12 Extract",
            title="Registered Land Record (7/12 Extract)",
            status=e_712_status,
            source_reference="Revenue Authority Record" if has_712 else None
        ))

        # Deed
        e_deed_status = "MISSING"
        if has_deed:
            ver_count = db.query(EvidenceRecord).filter(
                EvidenceRecord.project_id == project_id,
                EvidenceRecord.verification_status == "Verified"
            ).count()
            e_deed_status = "VERIFIED" if ver_count > 0 else "AVAILABLE"

        evidence_items.append(RequiredEvidenceItem(
            document_type="Sale Deed",
            title="Registered Conveyance / Deed",
            status=e_deed_status,
            source_reference="Sub-Registrar Office Record" if has_deed else None
        ))

        # Grounding in verified Procedure KB
        procedure_grounding = {
            "applicable_procedure": "RFCTLARR Act 2013 - Section 11 Notification & Inquiry Procedure",
            "source": "Maharashtra Land Acquisition Manual 2018",
            "section": "Section 11(1) & Section 15 Objections",
            "effective_date": "2018-01-01"
        }

        # Pending decision records
        pending = db.query(OfficerDecision).filter(
            OfficerDecision.project_id == project_id,
            OfficerDecision.decision_status.in_(["RECOMMENDED", "REVIEWED", "ACTION_INITIATED", "AWAITING_OUTCOME"])
        ).all()

        return DecisionContextResponse(
            project_id=project_id,
            decision_priority=priority,
            risk_level=exp.risk_level,
            predicted_probability=exp.predicted_probability,
            horizon_days=exp.prediction_horizon_days,
            summary=exp.summary,
            top_drivers=[d.dict() for d in exp.top_drivers],
            primary_bottleneck=btn.primary_bottleneck if btn else "Ownership Verification",
            bottleneck_severity=btn.severity if btn else "Low",
            interventions=[i.dict() for i in interventions_res],
            required_evidence=evidence_items,
            uncertainties=[u.dict() for u in exp.uncertainties],
            procedure_grounding=procedure_grounding,
            pending_decisions=[{
                "decision_id": p.decision_id,
                "decision_type": p.decision_type,
                "decision_status": p.decision_status,
                "selected_action": p.selected_action,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in pending]
        )


class OfficerWorkflowService:
    @staticmethod
    def create_decision(db: Session, project_id: str, decision_in: OfficerDecisionCreate, officer_id: str) -> OfficerDecision:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Isolation check: verify prediction and intervention belong to project
        if decision_in.prediction_id:
            pred = db.query(ProjectPrediction).filter(ProjectPrediction.prediction_id == decision_in.prediction_id).first()
            if not pred or pred.project_id != project_id:
                raise HTTPException(status_code=400, detail="Invalid prediction reference for project")

        if decision_in.intervention_id:
            intv = db.query(InterventionCandidate).filter(InterventionCandidate.intervention_id == decision_in.intervention_id).first()
            if not intv or intv.project_id != project_id:
                raise HTTPException(status_code=400, detail="Invalid intervention reference for project")

        # Determine initial state transition based on decision type
        initial_status = "REVIEWED"
        if decision_in.decision_type == "ACCEPT_RECOMMENDATION":
            initial_status = "ACCEPTED"
        elif decision_in.decision_type == "REJECT_RECOMMENDATION":
            initial_status = "REJECTED"
        elif decision_in.decision_type == "DEFER":
            initial_status = "DEFERRED"

        dec = OfficerDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            prediction_id=decision_in.prediction_id,
            intervention_id=decision_in.intervention_id,
            officer_id=officer_id,
            decision_type=decision_in.decision_type,
            decision_status=initial_status,
            decision_reason=decision_in.decision_reason,
            selected_action=decision_in.selected_action,
            decision_context_json=json.dumps({"officer_id": officer_id, "type": decision_in.decision_type}),
            data_origin="synthetic"
        )
        db.add(dec)

        # Audit Event
        audit = DecisionAuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            actor_id=officer_id,
            actor_type="OFFICER",
            event_type="DECISION_CREATED",
            target_entity=dec.decision_id,
            event_metadata_json=json.dumps({"decision_type": dec.decision_type, "status": initial_status}),
            data_origin="synthetic"
        )
        db.add(audit)
        db.commit()
        db.refresh(dec)
        return dec

    @staticmethod
    def get_decisions(db: Session, project_id: str) -> List[OfficerDecision]:
        return db.query(OfficerDecision).filter(OfficerDecision.project_id == project_id).order_by(OfficerDecision.created_at.desc()).all()

    @staticmethod
    def create_action(db: Session, project_id: str, action_in: OfficerActionCreate, officer_id: str) -> OfficerAction:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if action_in.decision_id:
            dec = db.query(OfficerDecision).filter(OfficerDecision.decision_id == action_in.decision_id).first()
            if not dec or dec.project_id != project_id:
                raise HTTPException(status_code=400, detail="Invalid decision reference for project")
            # Update decision status state machine
            dec.decision_status = "ACTION_INITIATED"

        act = OfficerAction(
            action_id=f"ACT-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            decision_id=action_in.decision_id,
            officer_id=officer_id,
            action_type=action_in.action_type,
            description=action_in.description,
            target_entity=action_in.target_entity,
            status="INITIATED",
            data_origin="synthetic"
        )
        db.add(act)

        # Audit Event
        audit = DecisionAuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            actor_id=officer_id,
            actor_type="OFFICER",
            event_type="ACTION_INITIATED",
            target_entity=act.action_id,
            event_metadata_json=json.dumps({"action_type": act.action_type, "target": act.target_entity}),
            data_origin="synthetic"
        )
        db.add(audit)
        db.commit()
        db.refresh(act)
        return act

    @staticmethod
    def get_actions(db: Session, project_id: str) -> List[OfficerAction]:
        return db.query(OfficerAction).filter(OfficerAction.project_id == project_id).order_by(OfficerAction.created_at.desc()).all()

    @staticmethod
    def update_action_outcome(db: Session, project_id: str, action_id: str, outcome_in: ActionOutcomeUpdate, officer_id: str) -> OfficerAction:
        act = db.query(OfficerAction).filter(OfficerAction.action_id == action_id, OfficerAction.project_id == project_id).first()
        if not act:
            raise HTTPException(status_code=404, detail="Action record not found")

        act.outcome_status = outcome_in.outcome_status
        act.outcome_note = outcome_in.outcome_note
        act.status = "COMPLETED"

        if act.decision_id:
            dec = db.query(OfficerDecision).filter(OfficerDecision.decision_id == act.decision_id).first()
            if dec:
                dec.decision_status = "RESOLVED" if outcome_in.outcome_status == "RESOLVED" else "AWAITING_OUTCOME"

        audit = DecisionAuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            actor_id=officer_id,
            actor_type="OFFICER",
            event_type="OUTCOME_RECORDED",
            target_entity=act.action_id,
            event_metadata_json=json.dumps({"outcome_status": act.outcome_status}),
            data_origin="synthetic"
        )
        db.add(audit)
        db.commit()
        db.refresh(act)
        return act

    @staticmethod
    def get_audit_trail(db: Session, project_id: str) -> List[DecisionAuditEvent]:
        return db.query(DecisionAuditEvent).filter(DecisionAuditEvent.project_id == project_id).order_by(DecisionAuditEvent.timestamp.desc()).all()
