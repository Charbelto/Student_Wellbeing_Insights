import pytest
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("stud_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "stud_officer", "password": "pass"}, follow_redirects=True)
    return c


def test_students_page(officer_client):
    resp = officer_client.get("/students")
    assert resp.status_code == 200


def test_add_student_route(officer_client):
    resp = officer_client.post(
        "/students/add",
        data={
            "name": "Stu One",
            "student_id": "STU1",
            "degree_id": 1,
            "degree_name": "CS",
            "year": 1,
            "age_band": "18-21",
            "domicile": "UK",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
