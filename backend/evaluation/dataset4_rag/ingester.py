import os
import json
import logging
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeSource, KnowledgeChunk
from evaluation.dataset4_rag.validator import Dataset4Validator

logger = logging.getLogger(__name__)

class Dataset4IngestionService:
    @staticmethod
    def ingest_dataset(db: Session) -> dict:
        """
        Idempotently ingest Dataset 4 records into knowledge tables in the SQLite/PostgreSQL database.
        """
        # 1. Validate first
        val_result = Dataset4Validator.validate_and_repair()
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        validated_path = os.path.join(base_dir, "datasets", "dataset4_rag", "dataset4_government_procedure_rag.validated.json")

        with open(validated_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = data.get("documents", [])
        sources_added = 0
        chunks_added = 0
        duplicates_prevented = 0

        for doc in documents:
            source_id = doc["source_id"]
            
            # Check for existing source for idempotency
            existing_src = db.query(KnowledgeSource).filter(KnowledgeSource.source_id == source_id).first()
            if existing_src:
                # Update existing source fields to reflect dataset upgrades safely
                existing_src.title = doc["title"]
                existing_src.department = doc["department"]
                existing_src.state = doc.get("state") or "National"
                existing_src.source_url = doc.get("source_url")
                existing_src.document_type = doc["document_type"]
                existing_src.publication_date = doc.get("publication_date")
                existing_src.effective_date = doc.get("effective_date")
                existing_src.language = doc.get("language") or "en"
                db.flush()
                src = existing_src
                duplicates_prevented += 1
            else:
                src = KnowledgeSource(
                    source_id=source_id,
                    title=doc["title"],
                    department=doc["department"],
                    state=doc.get("state") or "National",
                    source_url=doc.get("source_url"),
                    document_type=doc["document_type"],
                    publication_date=doc.get("publication_date"),
                    effective_date=doc.get("effective_date"),
                    language=doc.get("language") or "en",
                    status="ACTIVE"
                )
                db.add(src)
                sources_added += 1
                db.flush()

            # Create or update chunks
            # For simplicity, each document content is ingested as a single chunk to preserve full context structure
            chunk_id = f"CHNK-{source_id}-01"
            existing_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.chunk_id == chunk_id).first()
            if existing_chunk:
                existing_chunk.chunk_text = doc["content"]
                db.flush()
            else:
                chunk = KnowledgeChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    chunk_text=doc["content"],
                    page_number="1",
                    section="Main Content"
                )
                db.add(chunk)
                chunks_added += 1
                db.flush()

        db.commit()

        return {
            "validation": val_result,
            "sources_added": sources_added,
            "chunks_added": chunks_added,
            "duplicates_prevented": duplicates_prevented
        }
