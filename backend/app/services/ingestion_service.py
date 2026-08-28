import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeSource, KnowledgeChunk

class KnowledgeIngestionService:
    @staticmethod
    def chunk_text(text: str, size: int = 600, overlap: int = 100) -> List[str]:
        if not text:
            return []
        words = text.split()
        chunks = []
        for i in range(0, len(words), size - overlap):
            chunk = " ".join(words[i:i + size])
            if chunk:
                chunks.append(chunk)
        return chunks

    @staticmethod
    def ingest_source(
        db: Session,
        title: str,
        department: str,
        state: str,
        source_url: str,
        document_type: str,
        content_text: str,
        publication_date: str = None,
        effective_date: str = None,
        language: str = "en"
    ) -> KnowledgeSource:
        source_id = f"KNS-{uuid.uuid4().hex[:12].upper()}"

        db_source = KnowledgeSource(
            source_id=source_id,
            title=title,
            department=department,
            state=state,
            source_url=source_url,
            document_type=document_type,
            publication_date=publication_date,
            effective_date=effective_date,
            language=language,
            status="ACTIVE"
        )
        db.add(db_source)
        db.commit()
        db.refresh(db_source)

        # Generate simple chunks
        chunks = KnowledgeIngestionService.chunk_text(content_text)
        for i, txt in enumerate(chunks):
            chunk_id = f"KNC-{uuid.uuid4().hex[:12].upper()}"
            db_chunk = KnowledgeChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                chunk_text=txt,
                page_number=str((i // 2) + 1),
                section=f"Section {i+1}"
            )
            db.add(db_chunk)
        db.commit()

        return db_source
