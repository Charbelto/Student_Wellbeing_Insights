import pytest
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("sub_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "sub_officer", "password": "pass"}, follow_redirects=True)
    return c


def test_submission_list_route_not_found(officer_client):
    resp = officer_client.get("/submissions/999")
    assert resp.status_code in (302, 404)
