from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_api():
    response = client.post(
        "/api/generate-workout",
        json={
            "user_id": "TEST001",
            "username": "Test User",
            "age": 21,
            "weight": 65,
            "goal": "general wellness",
            "intensity": "low",
            "experience": "beginner",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "TEST001"
    assert body["workout_plan"]
    assert body["nutrition_tip"]


def test_feedback_api():
    response = client.post(
        "/api/submit-feedback",
        json={
            "user_id": "TEST001",
            "feedback": "Add more rest and mobility work.",
        },
    )
    assert response.status_code == 200
    assert response.json()["updated_plan"]
