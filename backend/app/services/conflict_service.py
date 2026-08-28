import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.case import Case, LandParcel, CasePerson, CaseEvent
from app.models.document import Document, Evidence
from app.models.conflict import PotentialConflict

class ConflictDetectionService:
    @staticmethod
    def normalize_name(name: str) -> str:
        if not name:
            return ""
        # normalize repeated spaces, punctuation, case, and trim whitespace
        normalized = name.strip().lower()
        normalized = " ".join(normalized.split())
        for char in [".", ",", "-", "_", "/"]:
            normalized = normalized.replace(char, " ")
        return " ".join(normalized.split())

    @staticmethod
    def analyze_case_conflicts(db: Session, case_id: str):
        case_obj = db.query(Case).filter(Case.case_id == case_id).first()
        if not case_obj:
            return

        # Fetch records
        people = db.query(CasePerson).filter(CasePerson.case_id == case_id).all()
        land_parcels = db.query(LandParcel).filter(LandParcel.case_id == case_id).all()
        evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        documents = db.query(Document).filter(Document.case_id == case_id).all()
        events = db.query(CaseEvent).filter(CaseEvent.case_id == case_id).all()

        # Clear existing OPEN conflicts for this case to avoid stale states
        db.query(PotentialConflict).filter(
            PotentialConflict.case_id == case_id,
            PotentialConflict.status == "OPEN"
        ).delete()
        db.commit()

        detected_conflicts = []

        # 1. Rule: Name Variation
        # Compare people names with extracted document names if any name exists in metadata
        for cp in people:
            person_name = cp.person.full_name
            norm_person = ConflictDetectionService.normalize_name(person_name)
            
            for doc in documents:
                if doc.extracted_metadata:
                    try:
                        meta = json.loads(doc.extracted_metadata)
                        # We also search file text contents or specific fields if parsed
                        extracted_names = []
                        if "name" in meta and isinstance(meta["name"], dict):
                            extracted_names.append(meta["name"].get("value", ""))
                        
                        # Fallback simple scan of document metadata text
                        text_dump = doc.file_name + " " + (doc.extracted_metadata or "")
                        # Look for potential name matches that are close but not equal
                        for name_val in extracted_names:
                            if name_val:
                                norm_extracted = ConflictDetectionService.normalize_name(name_val)
                                if norm_person != norm_extracted and (norm_person in norm_extracted or norm_extracted in norm_person):
                                    detected_conflicts.append({
                                        "conflict_type": "NAME_VARIATION",
                                        "description": f"Potential name variation detected. Case record name: '{person_name}'. Extracted document name: '{name_val}'.",
                                        "source_entity_a": cp.id,
                                        "source_entity_b": doc.document_id
                                    })
                    except Exception:
                        pass

        # 2. Rule: Date Discrepancy
        # Compare extracted document dates vs actual submission/creation events
        for doc in documents:
            if doc.extracted_metadata:
                try:
                    meta = json.loads(doc.extracted_metadata)
                    issue_date_meta = meta.get("issue_date")
                    if issue_date_meta and isinstance(issue_date_meta, dict):
                        issue_date_str = issue_date_meta.get("value")
                        if issue_date_str:
                            issue_dt = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
                            
                            # Document issue date cannot succeed upload or creation date
                            if case_obj.created_at:
                                created_date = case_obj.created_at.date()
                                if issue_dt > created_date:
                                    detected_conflicts.append({
                                        "conflict_type": "DATE_DISCREPANCY",
                                        "description": f"Potential date discrepancy: Document issue date ({issue_date_str}) succeeds case creation date ({created_date.isoformat()}).",
                                        "source_entity_a": doc.document_id,
                                        "source_entity_b": case_obj.case_id
                                    })
                except Exception:
                    pass

        # 3. Rule: Survey/Parcel Variation
        # Compare land parcel survey numbers with document extracted survey numbers
        for lp in land_parcels:
            if lp.survey_number:
                norm_lp_survey = lp.survey_number.strip().replace(" ", "")
                for doc in documents:
                    if doc.extracted_metadata:
                        try:
                            meta = json.loads(doc.extracted_metadata)
                            doc_survey_meta = meta.get("survey_number")
                            if doc_survey_meta and isinstance(doc_survey_meta, dict):
                                doc_survey = doc_survey_meta.get("value")
                                if doc_survey:
                                    norm_doc_survey = doc_survey.strip().replace(" ", "")
                                    if norm_lp_survey != norm_doc_survey:
                                        detected_conflicts.append({
                                            "conflict_type": "SURVEY_MISMATCH",
                                            "description": f"Potential parcel identifier mismatch: case land survey number ({lp.survey_number}) differs from document survey number ({doc_survey}).",
                                            "source_entity_a": lp.id,
                                            "source_entity_b": doc.document_id
                                        })
                        except Exception:
                            pass

        # 4. Rule: Document Number Variation
        # Compare registration / document numbers across different uploaded documents
        for i, doc_a in enumerate(documents):
            for doc_b in documents[i+1:]:
                if doc_a.extracted_metadata and doc_b.extracted_metadata:
                    try:
                        meta_a = json.loads(doc_a.extracted_metadata)
                        meta_b = json.loads(doc_b.extracted_metadata)
                        reg_a = meta_a.get("registration_number", {}).get("value")
                        reg_b = meta_b.get("registration_number", {}).get("value")
                        if reg_a and reg_b and reg_a != reg_b and doc_a.document_type == doc_b.document_type:
                            detected_conflicts.append({
                                "conflict_type": "DOCUMENT_NUMBER_MISMATCH",
                                "description": f"Potential document number mismatch: '{doc_a.file_name}' registration ({reg_a}) differs from '{doc_b.file_name}' registration ({reg_b}).",
                                "source_entity_a": doc_a.document_id,
                                "source_entity_b": doc_b.document_id
                            })
                    except Exception:
                        pass

        # 5. Rule: Potential Duplicate Document
        # Same registration number, document type and upload date matching
        for i, doc_a in enumerate(documents):
            for doc_b in documents[i+1:]:
                if doc_a.extracted_metadata and doc_b.extracted_metadata:
                    try:
                        meta_a = json.loads(doc_a.extracted_metadata)
                        meta_b = json.loads(doc_b.extracted_metadata)
                        reg_a = meta_a.get("registration_number", {}).get("value")
                        reg_b = meta_b.get("registration_number", {}).get("value")
                        if reg_a and reg_b and reg_a == reg_b and doc_a.document_type == doc_b.document_type:
                            detected_conflicts.append({
                                "conflict_type": "POTENTIAL_DUPLICATE_DOCUMENT",
                                "description": f"Potential duplicate document: Multiple '{doc_a.document_type}' uploads share registration number ({reg_a}).",
                                "source_entity_a": doc_a.document_id,
                                "source_entity_b": doc_b.document_id
                            })
                    except Exception:
                        pass

        # 6. Rule: Hash/Content Discrepancy (from comparison logs)
        # Scan comparisons from events
        for evt in events:
            if evt.event_type == "DOCUMENT_COMPARED" and evt.metadata_json:
                try:
                    meta = json.loads(evt.metadata_json)
                    match = meta.get("match")
                    text_diff = meta.get("text_diff_detected")
                    doc_a_id = meta.get("document_id_a")
                    doc_b_id = meta.get("document_id_b")
                    if match is False:
                        desc = "Documents differ — review required."
                        if text_diff is True:
                            desc += " Potential content difference detected."
                        detected_conflicts.append({
                            "conflict_type": "HASH_DISCREPANCY",
                            "description": desc,
                            "source_entity_a": doc_a_id,
                            "source_entity_b": doc_b_id
                        })
                except Exception:
                    pass

        # 7. Rule: Missing Expected Evidence
        # If a comparison comparison has been logged/initiated via timeline event, counterpart is expected
        initiated_comparison = any(evt.event_type == "DOCUMENT_COMPARED" for evt in events)
        citizen_uploads = [e for e in evidence_list if e.evidence_type == "CITIZEN_SUBMISSION"]
        officer_counterparts = [e for e in evidence_list if e.evidence_type == "OFFICIAL_COUNTERPART"]
        if initiated_comparison and citizen_uploads and not officer_counterparts:
            detected_conflicts.append({
                "conflict_type": "MISSING_COUNTERPART",
                "description": "Official counterpart not available.",
                "source_entity_a": case_id,
                "source_entity_b": None
            })

        # Save and deduplicate using idempotency keys
        for c in detected_conflicts:
            # Deterministic conflict id creation from signature
            sign_str = f"{case_id}:{c['conflict_type']}:{c['source_entity_a']}:{c['source_entity_b']}"
            import hashlib
            conflict_uuid = f"CON-{hashlib.sha256(sign_str.encode('utf-8')).hexdigest()[:12].upper()}"

            existing = db.query(PotentialConflict).filter(PotentialConflict.conflict_id == conflict_uuid).first()
            if not existing:
                db_conflict = PotentialConflict(
                    conflict_id=conflict_uuid,
                    case_id=case_id,
                    conflict_type=c["conflict_type"],
                    severity="REVIEW_REQUIRED",
                    description=c["description"],
                    status="OPEN",
                    source_entity_a=c["source_entity_a"],
                    source_entity_b=c["source_entity_b"]
                )
                db.add(db_conflict)
        db.commit()
