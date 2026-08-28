import pytest
import os
from app.models.user import User
from app.models.case import Case, LandParcel, Person, CasePerson, CaseEvent
from app.models.document import Document, Evidence
from app.core.database import SessionLocal
from evaluation.dataset4_rag.validator import Dataset4Validator
from evaluation.dataset4_rag.ingester import Dataset4IngestionService
from app.models.knowledge import KnowledgeSource, KnowledgeChunk
from app.services.rag_service import RAGService

def test_dataset4_validation():
    result = Dataset4Validator.validate_and_repair()
    assert result["original_parse_status"] == "SUCCESS"
    assert result["original_record_count"] == 36
    assert result["validated_record_count"] == 36
    
    # Assert validated target file exists
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    validated_path = os.path.join(base_dir, "datasets", "dataset4_rag", "dataset4_government_procedure_rag.validated.json")
    assert os.path.exists(validated_path)

def test_dataset4_ingestion_and_idempotency():
    db = SessionLocal()
    # Clean prior database sources/chunks to verify additions count
    db.query(KnowledgeChunk).delete()
    db.query(KnowledgeSource).delete()
    db.commit()
    
    # Trigger Ingestion
    ingest_result = Dataset4IngestionService.ingest_dataset(db)
    assert ingest_result["chunks_added"] == 36
    
    # Trigger second run to test idempotency
    second_run = Dataset4IngestionService.ingest_dataset(db)
    assert second_run["sources_added"] == 0
    assert second_run["chunks_added"] == 0
    assert second_run["duplicates_prevented"] == 36
    db.close()

def test_dataset4_rag_service_smoke_test():
    db = SessionLocal()
    
    # Query with matched criteria
    case_context = {
        "case_type": "7/12 / Land Record",
        "description": "ObtainingSatbaraUtara",
        "village": "Vitthalwadi",
        "taluka": "Shrigonda",
        "district": "Ahmednagar"
    }
    
    guidance = RAGService.generate_grounded_guidance(db, case_context, "How do I view online Satbara Utara?")
    assert guidance["answer"] is not None
    assert len(guidance["sources"]) > 0
    assert "https://bhulekh.mahabhumi.gov.in/" in [s["source_url"] for s in guidance["sources"]]

    # Query with no match fallback
    fallback_guidance = RAGService.generate_grounded_guidance(db, {}, "NonExistentTopicRandomCode")
    assert fallback_guidance["answer"] == "No relevant government guidance is currently available in the system repository."
    assert len(fallback_guidance["sources"]) == 0

    db.close()

def test_dataset4_production_isolation():
    # Verify that no test cases exist using Dataset 4 values in production tables
    from app.core.database import SessionLocal
    from app.models.case import Case
    from app.models.document import Document
    db = SessionLocal()
    
    # Ingest does not create case or document instances
    assert db.query(Case).filter(Case.title == "Mahabhulekh Portal - 7/12 Extract Online Viewing Service").first() is None
    assert db.query(Document).filter(Document.file_name == "dataset4_government_procedure_rag.json").first() is None
    
    # Teardown: Clean up Database to prevent test pollution in other RAG test suites
    db.query(KnowledgeChunk).delete()
    db.query(KnowledgeSource).delete()
    db.commit()
    db.close()
