import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "shikshaflow-api"}

def test_get_teacher():
    response = client.get("/api/v1/teachers/teacher-demo-001")
    assert response.status_code == 200
    assert response.json()["name"] == "Priya Sharma"

def test_get_classes():
    response = client.get("/api/v1/teachers/teacher-demo-001/classes")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == "class-7a"

def test_create_task_validation():
    # Test invalid duration
    payload = {
        "teacher_id": "teacher-demo-001",
        "class_id": "class-7a",
        "subject": "Math",
        "topic": "Algebra",
        "duration_minutes": -10,
        "language": "mr"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422

    # Test invalid language
    payload["duration_minutes"] = 40
    payload["language"] = "fr"  # Invalid language
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422

    # Test nonexistent class
    payload["language"] = "mr"
    payload["class_id"] = "class-nonexistent"
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 404

def test_task_lifecycle():
    # Create task
    payload = {
        "teacher_id": "teacher-demo-001",
        "class_id": "class-7a",
        "subject": "Mathematics",
        "topic": "Fractions",
        "duration_minutes": 45,
        "language": "mr"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 200
    task = response.json()
    assert task["id"].startswith("TASK-")
    assert task["status"] == "draft"

    # Get task
    response = client.get(f"/api/v1/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json()["topic"] == "Fractions"

    # Update task
    update_payload = {"topic": "Decimals and Fractions", "duration_minutes": 30}
    response = client.patch(f"/api/v1/tasks/{task['id']}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["topic"] == "Decimals and Fractions"
    assert response.json()["duration_minutes"] == 30

    # List tasks
    response = client.get("/api/v1/teachers/teacher-demo-001/tasks")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(t["id"] == task["id"] for t in response.json())
