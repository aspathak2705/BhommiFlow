import pytest
import os
from sqlalchemy.orm import Session
from app.models.case import Case
from evaluation.document_comparison.loader import Dataset3Loader
from evaluation.document_comparison.evaluator import DocumentComparisonEvaluator
from evaluation.document_comparison.metrics import EvaluationMetricsCalculator

def test_dataset3_loader():
    records = Dataset3Loader.load_dataset()
    assert len(records) == 100
    assert records[0]["comparison_id"] == "BF-CMP-4E810C97"
    assert "comparison_payload" in records[0]

def test_dataset3_evaluator_and_metrics():
    records = Dataset3Loader.load_dataset()
    predictions = [DocumentComparisonEvaluator.evaluate_scenario(r) for r in records]
    
    assert len(predictions) == 100
    metrics = EvaluationMetricsCalculator.calculate(records, predictions)
    
    assert metrics["total_records"] == 100
    assert metrics["evaluable_records"] == 100
    assert metrics["precision"] > 0.8
    assert metrics["recall"] > 0.8
    assert metrics["f1_score"] > 0.8
    assert metrics["rule_consistency"] == 0.88

def test_dataset3_production_isolation():
    # Verify that no test cases exist using Dataset 3 values in backend storage/DB
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.document import Document, Evidence
    from app.models.conflict import PotentialConflict
    from app.models.workflow import EvidenceRequest, Notification
    db = SessionLocal()
    
    # Query database to ensure no comparison ID from dataset 3 is present
    records = Dataset3Loader.load_dataset()
    for r in records[:5]:
        case_check = db.query(Case).filter(Case.case_id == r["comparison_id"]).first()
        assert case_check is None
        
    db.close()
