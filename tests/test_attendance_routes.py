import pytest
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("route_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "route_officer", "password": "pass"}, follow_redirects=True)
    return c


def test_api_students_officer_can_access(officer_client, db_setup, student_service):
    student_service.create_student("Route Student", "RS1")
    resp = officer_client.get("/api/students")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(s["student_id"] == "RS1" for s in data)


def test_export_risk_officer(officer_client):
    resp = officer_client.get("/export/risk")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("Content-Type", "")
