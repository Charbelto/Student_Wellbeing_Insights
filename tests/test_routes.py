import pytest
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("route_officer_main", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "route_officer_main", "password": "pass"}, follow_redirects=True)
    return c


def test_home_redirects(officer_client):
    resp = officer_client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 303)
