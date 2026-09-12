import os
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeSource, KnowledgeChunk

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def get_dataset_dir() -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "datasets")

    @classmethod
    def ingest_d1_cases(cls, db: Session, limit: int = 0) -> dict:
        d1_file = os.path.join(cls.get_dataset_dir(), "dataset1_land_cases", "cases.jsonl")
        if not os.path.exists(d1_file):
            return {"sources_added": 0, "chunks_added": 0, "status": "FILE_NOT_FOUND"}

        existing_source_ids = set(r[0] for r in db.query(KnowledgeSource.source_id).filter(KnowledgeSource.document_type == "D1_CASE").all())
        existing_chunk_ids = set(r[0] for r in db.query(KnowledgeChunk.chunk_id).filter(KnowledgeChunk.chunk_id.like("D1:%")).all())

        new_sources = []
        new_chunks = []
        duplicates_prevented = 0
        count = 0

        with open(d1_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                if limit > 0 and count >= limit:
                    break
                count += 1
                record = json.loads(line.strip())
                case_id = record["case_id"]
                source_id = f"D1:{case_id}"

                persons_str = ", ".join([f"{p.get('name')} ({p.get('role')})" for p in record.get("persons", [])])
                parcels_str = ", ".join([f"{p.get('survey_number')} in {p.get('village')}" for p in record.get("parcels", [])])
                docs_str = ", ".join([f"{d.get('document_type')} ({d.get('document_number')})" for d in record.get("documents", [])])
                conflicts_str = "; ".join([f"{c.get('conflict_type')}: {c.get('description')}" for c in record.get("conflicts", [])])
                events_str = "; ".join([f"{e.get('event_type')} on {e.get('event_date')}" for e in record.get("events", [])])

                text_content = (
                    f"Case ID: {case_id}\n"
                    f"Case Type: {record.get('case_type')}\n"
                    f"Archetype Focus: {record.get('case_archetype_focus')}\n"
                    f"Status: {record.get('case_status')} | Complexity: {record.get('case_complexity')} | Priority: {record.get('priority')}\n"
                    f"Location: {record.get('village')}, {record.get('taluka')}, {record.get('district')}\n"
                    f"Land Type: {record.get('land_type')}\n"
                    f"Description: {record.get('description')}\n"
                    f"Persons: {persons_str}\n"
                    f"Parcels: {parcels_str}\n"
                    f"Documents: {docs_str}\n"
                    f"Events Timeline: {events_str}\n"
                    f"Conflict Context: {conflicts_str}\n"
                )

                if source_id in existing_source_ids:
                    duplicates_prevented += 1
                else:
                    new_sources.append(KnowledgeSource(
                        source_id=source_id,
                        title=f"Case {case_id}: {record.get('case_type')}",
                        department="Land Records Case Intelligence",
                        state=record.get("district") or "National",
                        source_url=f"bhoomi://cases/{case_id}",
                        document_type="D1_CASE",
                        status="ACTIVE"
                    ))
                    existing_source_ids.add(source_id)

                chunk_id = f"D1:{case_id}:01"
                if chunk_id not in existing_chunk_ids:
                    new_chunks.append(KnowledgeChunk(
                        chunk_id=chunk_id,
                        source_id=source_id,
                        chunk_text=text_content,
                        page_number="1",
                        section=f"CASE_ID:{case_id}|DISTRICT:{record.get('district')}|TALUKA:{record.get('taluka')}"
                    ))
                    existing_chunk_ids.add(chunk_id)

        if new_sources:
            db.add_all(new_sources)
        if new_chunks:
            db.add_all(new_chunks)
        db.commit()

        return {"sources_added": len(new_sources), "chunks_added": len(new_chunks), "duplicates_prevented": duplicates_prevented}

    @classmethod
    def ingest_d2_documents(cls, db: Session, limit: int = 0) -> dict:
        d2_file = os.path.join(cls.get_dataset_dir(), "dataset2_document_extraction", "dataset_2000.jsonl")
        if not os.path.exists(d2_file):
            return {"sources_added": 0, "chunks_added": 0, "status": "FILE_NOT_FOUND"}

        existing_source_ids = set(r[0] for r in db.query(KnowledgeSource.source_id).filter(KnowledgeSource.document_type == "D2_DOCUMENT").all())
        existing_chunk_ids = set(r[0] for r in db.query(KnowledgeChunk.chunk_id).filter(KnowledgeChunk.chunk_id.like("D2:%")).all())

        new_sources = []
        new_chunks = []
        duplicates_prevented = 0
        count = 0

        with open(d2_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                if limit > 0 and count >= limit:
                    break
                count += 1
                doc = json.loads(line.strip())
                doc_id = doc["document_id"]
                source_id = f"D2:{doc_id}"

                ocr_text = doc.get("ocr_text") or "EMPTY_OCR"
                ground_truth = doc.get("ground_truth_json") or {}
                gt_str = json.dumps(ground_truth, ensure_ascii=False) if ground_truth else "EMPTY_GROUND_TRUTH"
                persons_str = ", ".join(doc.get("person_names") or [])

                text_content = (
                    f"Document ID: {doc_id}\n"
                    f"Document Type: {doc.get('document_type')}\n"
                    f"Document Status: {doc.get('document_status')} | Issuer: {doc.get('issuer')}\n"
                    f"Location: {doc.get('village')}, {doc.get('taluka')}, {doc.get('district')}\n"
                    f"Survey Number: {doc.get('survey_number')} | Subdivision: {doc.get('subdivision_number')}\n"
                    f"Persons Mentioned: {persons_str}\n"
                    f"Issue Date: {doc.get('issue_date')} | Registration Date: {doc.get('registration_date')}\n"
                    f"Structured Ground Truth: {gt_str}\n"
                    f"OCR Text:\n{ocr_text}\n"
                )

                if source_id in existing_source_ids:
                    duplicates_prevented += 1
                else:
                    new_sources.append(KnowledgeSource(
                        source_id=source_id,
                        title=f"Document {doc_id}: {doc.get('document_type')}",
                        department=doc.get("issuer") or "Revenue Department",
                        state=doc.get("district") or "National",
                        source_url=f"bhoomi://documents/{doc_id}",
                        document_type="D2_DOCUMENT",
                        status="ACTIVE"
                    ))
                    existing_source_ids.add(source_id)

                chunk_id = f"D2:{doc_id}:01"
                if chunk_id not in existing_chunk_ids:
                    new_chunks.append(KnowledgeChunk(
                        chunk_id=chunk_id,
                        source_id=source_id,
                        chunk_text=text_content,
                        page_number="1",
                        section=f"DOC_ID:{doc_id}|DISTRICT:{doc.get('district')}|TALUKA:{doc.get('taluka')}"
                    ))
                    existing_chunk_ids.add(chunk_id)

        if new_sources:
            db.add_all(new_sources)
        if new_chunks:
            db.add_all(new_chunks)
        db.commit()

        return {"sources_added": len(new_sources), "chunks_added": len(new_chunks), "duplicates_prevented": duplicates_prevented}

    @classmethod
    def ingest_d3_comparisons(cls, db: Session, limit: int = 0) -> dict:
        d3_file = os.path.join(cls.get_dataset_dir(), "dataset3_document_comparison", "dataset_3000.jsonl")
        if not os.path.exists(d3_file):
            return {"sources_added": 0, "chunks_added": 0, "status": "FILE_NOT_FOUND"}

        existing_source_ids = set(r[0] for r in db.query(KnowledgeSource.source_id).filter(KnowledgeSource.document_type == "D3_COMPARISON").all())
        existing_chunk_ids = set(r[0] for r in db.query(KnowledgeChunk.chunk_id).filter(KnowledgeChunk.chunk_id.like("D3:%")).all())

        new_sources = []
        new_chunks = []
        duplicates_prevented = 0
        count = 0

        with open(d3_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                if limit > 0 and count >= limit:
                    break
                count += 1
                cmp = json.loads(line.strip())
                cmp_id = cmp["comparison_id"]
                source_id = f"D3:{cmp_id}"

                payload = cmp.get("comparison_payload", {})
                derived = cmp.get("derived_features", {})
                loc = cmp.get("location", {})

                text_content = (
                    f"Comparison ID: {cmp_id}\n"
                    f"Document Type: {cmp.get('document_type')}\n"
                    f"Document A: {cmp.get('document_a_id')} | Document B: {cmp.get('document_b_id')}\n"
                    f"Scenario: {cmp.get('comparison_scenario')} | Difficulty: {cmp.get('comparison_difficulty')}\n"
                    f"Location: {loc.get('village')}, {loc.get('taluka')}, {loc.get('district')}\n"
                    f"Content Difference: {payload.get('content_difference')}\n"
                    f"Name Diff: {payload.get('name_difference')} | Number Diff: {payload.get('number_difference')}\n"
                    f"Address Diff: {payload.get('address_difference')} | Survey Diff: {payload.get('survey_difference')}\n"
                    f"High Severity Conflict Count: {derived.get('high_severity_conflict_count', 0)}\n"
                    f"Review Required: {derived.get('review_required', False)}\n"
                )

                if source_id in existing_source_ids:
                    duplicates_prevented += 1
                else:
                    new_sources.append(KnowledgeSource(
                        source_id=source_id,
                        title=f"Comparison {cmp_id}: {cmp.get('document_type')}",
                        department="Evidence Intelligence Discrepancy Service",
                        state=loc.get("district") or "National",
                        source_url=f"bhoomi://comparisons/{cmp_id}",
                        document_type="D3_COMPARISON",
                        status="ACTIVE"
                    ))
                    existing_source_ids.add(source_id)

                chunk_id = f"D3:{cmp_id}:01"
                if chunk_id not in existing_chunk_ids:
                    new_chunks.append(KnowledgeChunk(
                        chunk_id=chunk_id,
                        source_id=source_id,
                        chunk_text=text_content,
                        page_number="1",
                        section=f"CMP_ID:{cmp_id}|DOC_A:{cmp.get('document_a_id')}|DOC_B:{cmp.get('document_b_id')}"
                    ))
                    existing_chunk_ids.add(chunk_id)

        if new_sources:
            db.add_all(new_sources)
        if new_chunks:
            db.add_all(new_chunks)
        db.commit()

        return {"sources_added": len(new_sources), "chunks_added": len(new_chunks), "duplicates_prevented": duplicates_prevented}

    @classmethod
    def ingest_d4_procedures(cls, db: Session, limit: int = 0) -> dict:
        d4_dir = os.path.join(cls.get_dataset_dir(), "dataset4_rag")
        validated_file = os.path.join(d4_dir, "dataset4_government_procedure_rag.validated.json")
        if not os.path.exists(validated_file):
            validated_file = os.path.join(d4_dir, "dataset4_government_procedure_rag.json")

        if not os.path.exists(validated_file):
            return {"sources_added": 0, "chunks_added": 0, "status": "FILE_NOT_FOUND"}

        with open(validated_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = data.get("documents", [])
        existing_source_ids = set(r[0] for r in db.query(KnowledgeSource.source_id).all())
        existing_chunk_ids = set(r[0] for r in db.query(KnowledgeChunk.chunk_id).filter(KnowledgeChunk.chunk_id.like("D4:%")).all())

        new_sources = []
        new_chunks = []
        duplicates_prevented = 0
        count = 0

        for doc in documents:
            if limit > 0 and count >= limit:
                break
            count += 1
            source_id = doc["source_id"]
            if source_id in existing_source_ids:
                duplicates_prevented += 1
            else:
                new_sources.append(KnowledgeSource(
                    source_id=source_id,
                    title=doc["title"],
                    department=doc["department"],
                    state=doc.get("state") or "National",
                    source_url=doc.get("source_url"),
                    document_type="D4_PROCEDURE",
                    publication_date=doc.get("publication_date"),
                    effective_date=doc.get("effective_date"),
                    language=doc.get("language") or "en",
                    status="ACTIVE"
                ))
                existing_source_ids.add(source_id)

            chunk_id = f"D4:{source_id}:01"
            if chunk_id not in existing_chunk_ids:
                new_chunks.append(KnowledgeChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    chunk_text=doc["content"],
                    page_number="1",
                    section="Main Procedure Content"
                ))
                existing_chunk_ids.add(chunk_id)

        if new_sources:
            db.add_all(new_sources)
        if new_chunks:
            db.add_all(new_chunks)
        db.commit()

        return {"sources_added": len(new_sources), "chunks_added": len(new_chunks), "duplicates_prevented": duplicates_prevented}

    @classmethod
    def ingest_all(cls, db: Session, limit: int = 0) -> dict:
        d1_res = cls.ingest_d1_cases(db, limit=limit)
        d2_res = cls.ingest_d2_documents(db, limit=limit)
        d3_res = cls.ingest_d3_comparisons(db, limit=limit)
        d4_res = cls.ingest_d4_procedures(db, limit=limit)
        return {
            "D1": d1_res,
            "D2": d2_res,
            "D3": d3_res,
            "D4": d4_res
        }
