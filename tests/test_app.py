import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 3,
            "participants": ["alice@example.test"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 3,
            "participants": ["alice@example.test"],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client):
    # Arrange
    email = "bob@example.test"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up bob@example.test for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "alice@example.test"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == [email]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    email = "bob@example.test"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_signup_removes_participant(client):
    # Arrange
    email = "alice@example.test"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Removed alice@example.test from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_remove_signup_returns_404_for_unknown_activity(client):
    # Arrange
    email = "alice@example.test"

    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_signup_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "bob@example.test"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }