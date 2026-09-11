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
from app.schemas.explainability import ExplanationResponse, ExplanationDriver, UncertaintyItem, InterventionResponse
from app.services.prediction_service import DelayPredictionService, FeatureEngineeringService

HUMAN_LABEL_MAP = {
    "project_elapsed_days": "Project Elapsed Duration",
    "high_severity_conflict_count": "High-Severity Document Discrepancy Count",
    "unresolved_conflict_count": "Unresolved Conflict Count",
    "missing_document_count": "Pending/Unverified Document Count",
    "critical_path_blocked": "Critical Path Dependency Blockage",
    "bottleneck_age_days": "Primary Bottleneck Unresolved Duration",
    "bottleneck_is_ownership": "Ownership Verification Stage Delay",
    "bottleneck_is_legal": "Legal Resolution Stage Hold",
    "stage_is_compensation": "Compensation Assessment Active",
    "parcel_count": "Land Parcel Count"
}

class ExplainabilityService:
    @staticmethod
    def generate_explanation(db: Session, project_id: str) -> ExplanationResponse:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch latest prediction or generate if none exists
        pred = db.query(ProjectPrediction).filter(ProjectPrediction.project_id == project_id).order_by(ProjectPrediction.created_at.desc()).first()
        if not pred:
            pred_resp = DelayPredictionService.generate_prediction(db, project_id)
            pred = db.query(ProjectPrediction).filter(ProjectPrediction.prediction_id == pred_resp.prediction_id).first()

        top_feats = json.loads(pred.top_features_json) if pred.top_features_json else []

        drivers: List[ExplanationDriver] = []
        for feat in top_feats:
            fname = feat.get("feature", "")
            fval = float(feat.get("value", 0.0))
            fimp = float(feat.get("importance", 0.0))

            # Attempt evidence linkage
            supp_type = None
            supp_id = None
            if "conflict" in fname:
                cnf = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id).first()
                if cnf:
                    supp_type = "ConflictSignal"
                    supp_id = cnf.conflict_id
            elif "document" in fname:
                doc = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id).first()
                if doc:
                    supp_type = "BhoomiDocument"
                    supp_id = doc.document_id

            drivers.append(ExplanationDriver(
                feature_name=fname,
                observed_value=fval,
                importance=fimp,
                human_label=HUMAN_LABEL_MAP.get(fname, fname.replace("_", " ").title()),
                supporting_evidence_type=supp_type,
                supporting_source_id=supp_id
            ))

        # Build uncertainties list
        uncertainties: List[UncertaintyItem] = []
        pending_docs = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id, BhoomiDocument.extraction_status != "Completed").count()
        if pending_docs > 0:
            uncertainties.append(UncertaintyItem(
                title="Pending Document Extractions",
                description=f"{pending_docs} uploaded document(s) have unverified extractions.",
                impact="Document information requires officer review before legal reliance."
            ))

        unverified_ev = db.query(EvidenceRecord).filter(EvidenceRecord.project_id == project_id, EvidenceRecord.verification_status == "Unverified").count()
        if unverified_ev > 0:
            uncertainties.append(UncertaintyItem(
                title="Unverified Evidence Facts",
                description=f"{unverified_ev} extracted evidence fact(s) are currently unverified by an officer.",
                impact="Evidence support reflects machine extractions and non-causal decision-support signals."
            ))

        summary = f"Project '{project.project_name}' evaluates at {pred.risk_level} Risk ({(pred.predicted_probability * 100).toFixed(1) if hasattr(pred.predicted_probability, 'toFixed') else round(pred.predicted_probability*100, 1)}% probability of material delay within 180 days). Top drivers include {drivers[0].human_label if drivers else 'general timeline progress'}."

        db_exp = ProjectExplanation(
            explanation_id=f"EXP-{uuid.uuid4().hex[:12].upper()}",
            project_id=project_id,
            prediction_id=pred.prediction_id,
            explanation_version="v1",
            summary=summary,
            explanation_json=json.dumps({
                "drivers": [d.dict() for d in drivers],
                "uncertainties": [u.dict() for u in uncertainties]
            }),
            data_origin="synthetic"
        )
        db.add(db_exp)
        db.commit()

        return ExplanationResponse(
            explanation_id=db_exp.explanation_id,
            project_id=project_id,
            prediction_id=pred.prediction_id,
            explanation_version="v1",
            summary=summary,
            risk_level=pred.risk_level,
            predicted_probability=pred.predicted_probability,
            prediction_horizon_days=180,
            top_drivers=drivers,
            uncertainties=uncertainties,
            created_at=db_exp.created_at,
            data_origin="synthetic"
        )


class InterventionService:
    @staticmethod
    def generate_interventions(db: Session, project_id: str) -> List[InterventionResponse]:
        conflicts = db.query(ConflictSignal).filter(ConflictSignal.project_id == project_id, ConflictSignal.status == "Open").all()
        btn = db.query(BottleneckSignal).filter(BottleneckSignal.project_id == project_id).order_by(BottleneckSignal.generated_at.desc()).first()

        interventions = []

        # Rule 1: High severity conflicts -> Verify Survey/Ownership Discrepancies
        if conflicts:
            for cnf in conflicts:
                cand = InterventionCandidate(
                    intervention_id=f"INT-{uuid.uuid4().hex[:12].upper()}",
                    project_id=project_id,
                    bottleneck_id=btn.bottleneck_id if btn else None,
                    title=f"Review & Verify: {cnf.title}",
                    description=f"Human officer verification recommended for cross-record discrepancy: {cnf.description}",
                    target_bottleneck=btn.primary_bottleneck if btn else "Ownership Verification",
                    priority="High" if cnf.severity in ["High", "Critical"] else "Medium",
                    expected_process_effect="May unblock parcel verification and downstream compensation processing.",
                    required_evidence="Original 7/12 extract & registered sale deed records.",
                    rule_id="RULE-INT-01",
                    status="Recommended",
                    data_origin="synthetic"
                )
                db.add(cand)
                interventions.append(cand)

        # Rule 2: Unverified documents -> Request missing or verified document uploads
        pending_docs = db.query(BhoomiDocument).filter(BhoomiDocument.project_id == project_id, BhoomiDocument.extraction_status != "Completed").all()
        if pending_docs:
            cand = InterventionCandidate(
                intervention_id=f"INT-{uuid.uuid4().hex[:12].upper()}",
                project_id=project_id,
                bottleneck_id=btn.bottleneck_id if btn else None,
                title="Complete Pending Document Review",
                description=f"{len(pending_docs)} document(s) require officer review or re-extraction validation.",
                target_bottleneck="Documentation",
                priority="Medium",
                expected_process_effect="Ensures all parcel evidence facts are normalized for graph intelligence.",
                required_evidence="Government counterpart records.",
                rule_id="RULE-INT-02",
                status="Recommended",
                data_origin="synthetic"
            )
            db.add(cand)
            interventions.append(cand)

        db.commit()
        return [InterventionResponse.from_orm(i) for i in interventions]
