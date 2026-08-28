import sys
import io
import json
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, CitizenProfile, OfficerProfile
from app.models.case import Case, LandParcel, Person, CasePerson, CaseEvent
from app.models.document import Document, Evidence
from app.api.routes.auth import TOKEN_DB
from app.services.integrity_service import verify_hash_chain
from app.services.extraction_service import extract_metadata_from_text

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    db = SessionLocal()
    # Clean up leftovers
    db.query(CaseEvent).delete()
    db.query(CasePerson).delete()
    db.query(Person).delete()
    db.query(LandParcel).delete()
    db.query(Evidence).delete()
    db.query(Document).delete()
    db.query(Case).delete()
    db.query(CitizenProfile).delete()
    db.query(OfficerProfile).delete()
    db.query(User).delete()
    db.commit()

    # Create users
    cit1 = User(id="cit-1", username="citizen1", role="citizen")
    db.add(cit1)
    cit_prof1 = CitizenProfile(user_id="cit-1", full_name="Anoop Citizen", preferred_language="en")
    db.add(cit_prof1)

    cit2 = User(id="cit-2", username="citizen2", role="citizen")
    db.add(cit2)
    cit_prof2 = CitizenProfile(user_id="cit-2", full_name="John Citizen", preferred_language="en")
    db.add(cit_prof2)

    off1 = User(id="off-1", username="officer1", role="officer")
    db.add(off1)
    off_prof1 = OfficerProfile(
        user_id="off-1",
        full_name="Rajesh Officer",
        department="Land Records",
        designation="Talathi",
        office="Taluka Office",
        district="Pune",
        taluka="Haveli"
    )
    db.add(off_prof1)

    off2 = User(id="off-2", username="officer2", role="officer")
    db.add(off2)
    off_prof2 = OfficerProfile(
        user_id="off-2",
        full_name="Amit Officer",
        department="Land Records",
        designation="Talathi",
        office="Taluka Office",
        district="Pune",
        taluka="Haveli"
    )
    db.add(off_prof2)

    db.commit()
    db.close()

    # Populate token database for authentic session verification
    TOKEN_DB["token-cit-1"] = "cit-1"
    TOKEN_DB["token-cit-2"] = "cit-2"
    TOKEN_DB["token-off-1"] = "off-1"
    TOKEN_DB["token-off-2"] = "off-2"

    yield

    db = SessionLocal()
    db.query(CaseEvent).delete()
    db.query(CasePerson).delete()
    db.query(Person).delete()
    db.query(LandParcel).delete()
    db.query(Evidence).delete()
    db.query(Document).delete()
    db.query(Case).delete()
    db.query(CitizenProfile).delete()
    db.query(OfficerProfile).delete()
    db.query(User).delete()
    db.commit()
    db.close()
    TOKEN_DB.clear()

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "bhoomiflow-api"}

def test_registration_and_login():
    # Register
    reg_payload = {
        "username": "newuser",
        "password": "mypassword",
        "role": "citizen",
        "full_name": "New Citizen",
        "email": "new@citizen.com",
        "phone": "9999999999"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

    # Login
    login_payload = {
        "username": "newuser",
        "password": "mypassword"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_authentic_profile_session():
    # Valid session
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer token-cit-1"})
    assert response.status_code == 200
    assert response.json()["username"] == "citizen1"

    # Invalid session
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer token-invalid"})
    assert response.status_code == 401

def test_case_creation_and_isolation():
    # Citizen 1 creates case
    case_payload = {
        "case_type": "Mutation delay",
        "title": "Delayed mutation",
        "description": "Long delay in Wagholi",
        "district": "Pune",
        "taluka": "Haveli",
        "village": "Wagholi",
        "land_parcels": [
            {
                "district": "Pune",
                "taluka": "Haveli",
                "village": "Wagholi",
                "survey_number": "104"
            }
        ],
        "people": [
            {
                "full_name": "Kumar",
                "role": "owner"
            }
        ]
    }
    response = client.post("/api/v1/cases", json=case_payload, headers={"Authorization": "Bearer token-cit-1"})
    assert response.status_code == 200
    case_data = response.json()
    case_id = case_data["case_id"]

    # Citizen 1 can see their case
    response = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-cit-1"})
    assert response.status_code == 200

    # Citizen 2 is blocked from viewing Citizen 1's case
    response = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-cit-2"})
    assert response.status_code == 403

    # Officer 1 is blocked because the case is not assigned to them yet
    response = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-off-1"})
    assert response.status_code == 403

def test_officer_assignment_authorization():
    # Assign Case to Officer 1 in DB
    db = SessionLocal()
    db_case = db.query(Case).first()
    assert db_case is not None
    db_case.assigned_officer_id = "off-1"
    db.commit()
    case_id = db_case.case_id
    db.close()

    # Officer 1 can now view the case
    response = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-off-1"})
    assert response.status_code == 200

    # Officer 2 is blocked because it is explicitly assigned to Officer 1
    response = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-off-2"})
    assert response.status_code == 403

    # Officer 1 updates status
    status_payload = {"status": "UNDER_REVIEW", "note": "Assigned details verified"}
    response = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json=status_payload,
        headers={"Authorization": "Bearer token-off-1"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"

    # Officer 2 is blocked from updating status
    response = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json=status_payload,
        headers={"Authorization": "Bearer token-off-2"}
    )
    assert response.status_code == 403

def test_document_uploads_and_security():
    db = SessionLocal()
    case_obj = db.query(Case).first()
    case_id = case_obj.case_id
    db.close()

    # 1. Citizen 1 uploads valid file
    file_content = b"Sale Deed Date: 28/08/2026 Reg No: 98765 Survey No: 104"
    files = {"file": ("saledeed.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"document_type": "Sale Deed"}

    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data=data,
        files=files,
        headers={"Authorization": "Bearer token-cit-1"}
    )
    assert response.status_code == 200
    doc_data = response.json()
    assert doc_data["sha256_hash"] is not None
    assert doc_data["status"] == "READY"

    # Verify metadata regex parser extracted fields correctly
    meta = json.loads(doc_data["extracted_metadata"])
    assert meta["issue_date"]["value"] == "2026-08-28"
    assert meta["registration_number"]["value"] == "98765"
    assert meta["survey_number"]["value"] == "104"

    # 2. Citizen 2 blocked from uploading to Citizen 1's case
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data=data,
        files=files,
        headers={"Authorization": "Bearer token-cit-2"}
    )
    assert response.status_code == 403

    # 3. Invalid file type rejected
    bad_files = {"file": ("test.exe", io.BytesIO(b"binary"), "application/octet-stream")}
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data=data,
        files=bad_files,
        headers={"Authorization": "Bearer token-cit-1"}
    )
    assert response.status_code == 400

    # 4. Oversized file rejected
    huge_files = {"file": ("big.pdf", io.BytesIO(b"0" * (11 * 1024 * 1024)), "application/pdf")}
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data=data,
        files=huge_files,
        headers={"Authorization": "Bearer token-cit-1"}
    )
    assert response.status_code == 400

def test_document_comparison():
    db = SessionLocal()
    case_obj = db.query(Case).first()
    case_id = case_obj.case_id
    db.close()

    # Upload Doc A (Citizen)
    file_a = b"Exact match content"
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data={"document_type": "Sale Deed"},
        files={"file": ("fileA.pdf", io.BytesIO(file_a), "application/pdf")},
        headers={"Authorization": "Bearer token-cit-1"}
    )
    doc_a_id = response.json()["document_id"]

    # Upload Counterpart Doc B (Officer 1 - identical)
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data={"document_type": "Sale Deed"},
        files={"file": ("fileB.pdf", io.BytesIO(file_a), "application/pdf")},
        headers={"Authorization": "Bearer token-off-1"}
    )
    doc_b_id = response.json()["document_id"]

    # Upload Doc C (Different content)
    file_c = b"Different matching content"
    response = client.post(
        f"/api/v1/cases/{case_id}/documents",
        data={"document_type": "Sale Deed"},
        files={"file": ("fileC.pdf", io.BytesIO(file_c), "application/pdf")},
        headers={"Authorization": "Bearer token-off-1"}
    )
    doc_c_id = response.json()["document_id"]

    # Compare identical files
    response = client.post(
        f"/api/v1/documents/{doc_a_id}/compare",
        data={"counterpart_id": doc_b_id},
        headers={"Authorization": "Bearer token-off-1"}
    )
    assert response.status_code == 200
    assert response.json()["match"] is True
    assert response.json()["status_text"] == "EXACT FILE MATCH"
    assert response.json()["content_comparison_available"] is False

    # Compare differing files (Verify mismatch is not labeled fraud)
    response = client.post(
        f"/api/v1/documents/{doc_a_id}/compare",
        data={"counterpart_id": doc_c_id},
        headers={"Authorization": "Bearer token-off-1"}
    )
    assert response.status_code == 200
    assert response.json()["match"] is False
    assert "differ" in response.json()["status_text"].lower()
    assert "fraud" not in response.json()["status_text"].lower()
    assert response.json()["content_comparison_available"] is True
    assert response.json()["text_diff_detected"] is True
    assert "character difference" in response.json()["comparison_summary"].lower()

def test_hash_chain_integrity_and_tamper_detection():
    db = SessionLocal()
    case_obj = db.query(Case).first()
    case_id = case_obj.case_id
    
    # Verify existing event timeline matches the append-only hash chain
    assert verify_hash_chain(db, case_id) is True

    # Tamper with an event in the database
    tamper_event = db.query(CaseEvent).filter(CaseEvent.case_id == case_id).first()
    assert tamper_event is not None
    tamper_event.event_type = "TAMPERED_EVENT"
    db.commit()

    # Integrity verification must fail
    assert verify_hash_chain(db, case_id) is False
    db.close()

def test_date_extraction_provenance():
    # Test common Indian date formats normalization and regex sources
    res_slash = extract_metadata_from_text("Date of registration is 28/08/2026")
    assert res_slash["issue_date"]["value"] == "2026-08-28"

    res_dash = extract_metadata_from_text("Action registered on 28-08-2026")
    assert res_dash["issue_date"]["value"] == "2026-08-28"

    res_dot = extract_metadata_from_text("Dated 28.08.2026")
    assert res_dot["issue_date"]["value"] == "2026-08-28"
