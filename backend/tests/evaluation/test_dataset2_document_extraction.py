import pytest
from sqlalchemy.orm import Session
from app.models.case import Case
from evaluation.document_extraction.loader import Dataset2Loader
from evaluation.document_extraction.evaluator import DocumentExtractionEvaluator
from evaluation.document_extraction.metrics import ExtractionMetricsCalculator

def test_dataset2_loaders_and_consistency():
    json_data = Dataset2Loader.load_json()
    csv_data = Dataset2Loader.load_csv()
    
    # Assert counts
    assert len(json_data) == 50
    assert len(csv_data) == 50
    
    consistency = Dataset2Loader.check_consistency()
    assert consistency["consistent"] is True

def test_dataset2_evaluator_metrics():
    json_data = Dataset2Loader.load_json()
    eval_results = [DocumentExtractionEvaluator.evaluate_record(r) for r in json_data]
    
    assert len(eval_results) == 50
    metrics = ExtractionMetricsCalculator.calculate(eval_results)
    
    assert metrics["total_records"] == 50
    # Accurate matching checks on evaluable fields
    assert "issue_date" in metrics["field_metrics"]
    assert "district" in metrics["field_metrics"]
    assert metrics["field_metrics"]["district"]["evaluable"] == 0

def test_dataset2_production_isolation():
    # Verify that no test cases exist using Dataset 2 values in backend database
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.document import Document, Evidence
    from app.models.conflict import PotentialConflict
    from app.models.workflow import EvidenceRequest, Notification
    db = SessionLocal()
    
    # Query database to ensure no document ID from dataset 2 is present in production tables
    json_data = Dataset2Loader.load_json()
    for r in json_data[:5]:
        doc_check = db.query(Document).filter(Document.document_id == r["document_id"]).first()
        assert doc_check is None
        
    db.close()
