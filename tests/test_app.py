from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import pytest

client = TestClient(app)

# Fixture to reset activities after each test
@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_signup_success():
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]
    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    # Second signup
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_activity_full():
    # Basketball Team has max 15, currently 1 participant
    for i in range(14):
        client.post(f"/activities/Basketball%20Team/signup?email=user{i}@example.com")
    # Now full
    response = client.post("/activities/Basketball%20Team/signup?email=last@example.com")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered test@example.com from Basketball Team" in data["message"]
    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" not in data["Basketball Team"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball%20Team/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    assert "Student not signed up" in response.json()["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/unregister?email=test@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]