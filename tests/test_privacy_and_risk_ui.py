import pytest
from app.database.connection import get_db_connection
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("ui_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "ui_officer", "password": "pass"}, follow_redirects=True)
    return c


@pytest.fixture
def tutor_client(app, user_service):
    user_service.create_user("ui_tutor", "pass", Role.TUTOR)
    c = app.test_client()
    c.post("/login", data={"username": "ui_tutor", "password": "pass"}, follow_redirects=True)
    return c


def seed_risk_records(db_name: str):
    conn = get_db_connection(db_name)
    cur = conn.cursor()
    # High risk student with late submissions and high stress
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile, medical_information) VALUES('RISK1',1,'CS',1,'18-21','UK','notes')"
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES('RISK1', 'High Risk')")
    cur.execute("INSERT INTO risk_indicator(student_id, avg_stress, late_submissions, avg_mark, min_mark, max_mark, risk_level) VALUES('RISK1',4.5,3,60,40,75,'High')")

    # Medium risk record
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile, medical_information) VALUES('RISK2',1,'CS',1,'18-21','UK','notes')"
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES('RISK2', 'Medium Risk')")
    cur.execute("INSERT INTO risk_indicator(student_id, avg_stress, late_submissions, avg_mark, min_mark, max_mark, risk_level) VALUES('RISK2',3.0,1,65,50,78,'Medium')")

    conn.commit()
    conn.close()


def seed_dashboard_student(db_name: str):
    conn = get_db_connection(db_name)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES('DASHX',1,'CS',1,'18-21','UK')"
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES('DASHX', 'Dashboard Name')")
    cur.execute(
        "INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate) VALUES('DASHX', 1, 10, 8, 0.8)"
    )
    cur.execute(
        "INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES('DASHX', 1, 3, 7, 3)"
    )
    conn.commit()
    conn.close()


def test_officer_dashboard_highlights_risk(officer_client, db_setup, app):
    seed_risk_records(db_setup)
    app.analytics_service.db_name = db_setup

    resp = officer_client.get("/officer_dashboard")
    html = resp.get_data(as_text=True)
    assert "risk-high" in html
    assert "risk-medium" in html


def test_dashboard_hides_student_name(tutor_client, db_setup, app):
    seed_dashboard_student(db_setup)
    app.analytics_service.db_name = db_setup
    app.student_service.db_name = db_setup

    resp = tutor_client.get("/dashboard?student_id=DASHX")
    html = resp.get_data(as_text=True)
    assert "Dashboard Name" not in html  # name should be hidden
    assert "DASHX" in html  # student id still visible

