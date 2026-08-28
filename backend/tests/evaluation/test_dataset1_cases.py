import pytest
import os
from app.models.user import User
from app.models.case import Case, LandParcel, Person, CasePerson, CaseEvent
from app.models.document import Document, Evidence
from app.core.database import SessionLocal
from evaluation.dataset1_land_cases.loader import Dataset1Loader

def test_dataset1_loader_counts():
    cases = Dataset1Loader.load_dataset1()
    assert len(cases) == 100

def test_dataset1_global_uniqueness():
    cases = Dataset1Loader.load_dataset1()
    case_ids = [c["case_id"] for c in cases]
    assert len(case_ids) == len(set(case_ids))

def test_dataset1_internal_entity_relations():
    cases = Dataset1Loader.load_dataset1()
    all_validation_errors = []
    for c in cases:
        errors = Dataset1Loader.validate_relationships(c)
        all_validation_errors.extend(errors)
    
    # Assert relational structural integrity holds
    assert len(all_validation_errors) == 0

def test_dataset1_production_database_isolation():
    db = SessionLocal()
    cases = Dataset1Loader.load_dataset1()
    
    for c in cases:
        db_case = db.query(Case).filter(Case.case_id == c["case_id"]).first()
        # Verify completely isolated from live cases table
        assert db_case is None
        
    db.close()
