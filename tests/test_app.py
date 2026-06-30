import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset the in-memory activity data before each test."""
    original_state = copy.deepcopy(app_module.activities)

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))

    yield

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_all_activities():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app_module.app)
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Basketball Team/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Basketball Team"
    assert email in app_module.activities["Basketball Team"]["participants"]


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    client = TestClient(app_module.app)
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    # Arrange
    client = TestClient(app_module.app)
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.post("/activities/Unknown Activity/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
