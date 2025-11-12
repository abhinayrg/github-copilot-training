from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


client = TestClient(app)


def test_get_activities_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic expectations about the structure
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest-user@example.com"

    # Ensure clean start: remove if it already exists
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Confirm participant appears in activities
    r2 = client.get("/activities")
    assert r2.status_code == 200
    assert email in r2.json()[activity]["participants"]

    # Signup again should fail
    r_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert r_dup.status_code == 400

    # Unregister
    r3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 200
    assert "Unregistered" in r3.json().get("message", "")

    # Confirm removal
    r4 = client.get("/activities")
    assert email not in r4.json()[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = "nonexistent-user@example.com"

    # Ensure email is not registered
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 404
