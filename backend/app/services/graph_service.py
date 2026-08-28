import json
from sqlalchemy.orm import Session
from app.models.case import Case, LandParcel, CasePerson, CaseEvent
from app.models.document import Document, Evidence
from app.schemas.graph import GraphResponse, GraphNode, GraphEdge

def build_case_graph(db: Session, case_id: str) -> GraphResponse:
    # Fetch real records from PostgreSQL
    case_obj = db.query(Case).filter(Case.case_id == case_id).first()
    if not case_obj:
        return GraphResponse(nodes=[], edges=[])

    nodes = []
    edges = []

    # 1. Add Case node
    nodes.append(GraphNode(
        id=case_obj.case_id,
        type="CASE",
        label=case_obj.case_reference,
        details={
            "Title": case_obj.title,
            "Type": case_obj.case_type,
            "Priority": case_obj.priority,
            "Status": case_obj.status,
            "Created At": case_obj.created_at.isoformat() if case_obj.created_at else "Not available"
        }
    ))

    # 2. Add Person nodes and INVOLVES relationships
    people = db.query(CasePerson).filter(CasePerson.case_id == case_id).all()
    for cp in people:
        nodes.append(GraphNode(
            id=cp.id,
            type="PERSON",
            label=cp.person.full_name,
            details={
                "Name": cp.person.full_name,
                "Role": cp.role,
                "Phone": cp.person.phone or "Not available",
                "Email": cp.person.email or "Not available",
                "Address": cp.person.address or "Not available"
            }
        ))
        edges.append(GraphEdge(
            source=case_obj.case_id,
            target=cp.id,
            type="INVOLVES"
        ))

    # 3. Add LandParcel nodes and INVOLVES relationships
    land_parcels = db.query(LandParcel).filter(LandParcel.case_id == case_id).all()
    for lp in land_parcels:
        label = f"Survey {lp.survey_number or 'N/A'}"
        nodes.append(GraphNode(
            id=lp.id,
            type="LAND_PARCEL",
            label=label,
            details={
                "District": lp.district,
                "Taluka": lp.taluka,
                "Village": lp.village,
                "Survey Number": lp.survey_number or "Not available",
                "Subdivision": lp.subdivision_number or "Not available",
                "Area": f"{lp.area} {lp.area_unit}" if lp.area else "Not available"
            }
        ))
        edges.append(GraphEdge(
            source=case_obj.case_id,
            target=lp.id,
            type="INVOLVES"
        ))

    # 4. Add Document nodes and CONTAINS relationships
    documents = db.query(Document).filter(Document.case_id == case_id).all()
    for doc in documents:
        nodes.append(GraphNode(
            id=doc.document_id,
            type="DOCUMENT",
            label=doc.file_name,
            details={
                "Document Type": doc.document_type,
                "File Name": doc.file_name,
                "File Size": f"{doc.file_size} bytes",
                "Hash": doc.sha256_hash,
                "Status": doc.status,
                "Uploaded At": doc.uploaded_at.isoformat() if doc.uploaded_at else "Not available"
            }
        ))
        edges.append(GraphEdge(
            source=case_obj.case_id,
            target=doc.document_id,
            type="CONTAINS"
        ))

        # Check for extracted metadata relationships to people
        if doc.extracted_metadata:
            try:
                meta = json.loads(doc.extracted_metadata)
                name_meta = meta.get("name", {}).get("value")
                if name_meta:
                    for cp in people:
                        if cp.person.full_name.lower().strip() in name_meta.lower().strip():
                            edges.append(GraphEdge(
                                source=cp.id,
                                target=doc.document_id,
                                type="MENTIONED_IN"
                            ))
            except Exception:
                pass

    # 5. Add Evidence nodes and SUPPORTED_BY relationships
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    for ev in evidence_list:
        nodes.append(GraphNode(
            id=ev.evidence_id,
            type="EVIDENCE",
            label=ev.evidence_type,
            details={
                "Evidence Type": ev.evidence_type,
                "Status": ev.status,
                "Submitted At": ev.submitted_at.isoformat() if ev.submitted_at else "Not available"
            }
        ))
        edges.append(GraphEdge(
            source=ev.document_id,
            target=ev.evidence_id,
            type="SUPPORTED_BY"
        ))

    # 6. Add CaseEvent nodes and HAS_EVENT relationships
    events = db.query(CaseEvent).filter(CaseEvent.case_id == case_id).order_by(CaseEvent.timestamp.asc()).all()
    prev_event_id = None
    for evt in events:
        nodes.append(GraphNode(
            id=evt.event_id,
            type="EVENT",
            label=evt.event_type,
            details={
                "Event Type": evt.event_type,
                "Actor Role": evt.actor_role,
                "Timestamp": evt.timestamp.isoformat() if evt.timestamp else "Not available",
                "Signature": evt.current_event_hash or "Not available"
            }
        ))
        edges.append(GraphEdge(
            source=case_obj.case_id,
            target=evt.event_id,
            type="GENERATED"
        ))

        # Link chronologically sequential events
        if prev_event_id:
            edges.append(GraphEdge(
                source=prev_event_id,
                target=evt.event_id,
                type="FOLLOWED_BY"
            ))
        prev_event_id = evt.event_id

    return GraphResponse(nodes=nodes, edges=edges)
