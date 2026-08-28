import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, CitizenProfile, OfficerProfile
from app.models.case import Case, LandParcel, Person, CasePerson, CaseEvent
from app.api.routes.auth import TOKEN_DB

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    db = SessionLocal()
    # Clean up leftovers
    db.query(CaseEvent).delete()
    db.query(CasePerson).delete()
    db.query(Person).delete()
    db.query(LandParcel).delete()
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
