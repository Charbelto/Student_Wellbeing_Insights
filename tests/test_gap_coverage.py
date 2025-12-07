import csv
import io
import pytest
from datetime import datetime
from app.database.connection import get_db_connection
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("gap_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "gap_officer", "password": "pass"}, follow_redirects=True)
    return c


@pytest.fixture
def tutor_client(app, user_service):
    user_service.create_user("gap_tutor", "pass", Role.TUTOR)
    c = app.test_client()
    c.post("/login", data={"username": "gap_tutor", "password": "pass"}, follow_redirects=True)
    return c


def seed_core_student(db_name: str, student_id: str):
    conn = get_db_connection(db_name)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile, medical_information) VALUES(?,1,'CS',1,'18-21','UK','notes')",
        (student_id,),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", (student_id, "Gap Student"))
    cur.execute(
        "INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate) VALUES(?, ?, ?, ?, ?)",
        (student_id, 1, 10, 8, 0.8),
    )
    cur.execute(
        "INSERT INTO modules(module_id, degree_id, code, name, semester, lecture_day, lecture_time) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (1, 1, "CS101", "Intro CS", 1, "Mon", "09:00"),
    )
    cur.execute(
        "INSERT INTO submissions(submission_id, student_id, module_id, semester, deadline_datetime, submitted_datetime, early_late_submissions, mark, late) VALUES(?,?,?,?,?,?,?,?,?)",
        (1, student_id, 1, 1, "2023-10-10", "2023-10-11", 1, 70, 1),
    )
    # wellbeing surveys
    cur.execute(
        "INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES(?,?,?,?,?)",
        (student_id, 1, 3, 7, 3),
    )
    cur.execute(
        "INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES(?,?,?,?,?)",
        (student_id, 2, 4, 6, 2),
    )
    # feedback
    cur.execute(
        "INSERT INTO module_feedback(feedback_id, student_id, module_id, engaging_content, comfortable_asking_questions, pace_rating, prepared_for_exams, hours_outside_class) VALUES(?,?,?,?,?,?,?,?)",
        ("F1", student_id, 1, 4, 4, 3, 4, 5),
    )
    conn.commit()
    conn.close()


def test_dashboard_privacy_redaction(app, db_setup, officer_client, tutor_client):
    seed_core_student(db_setup, "DASH1")
    app.student_service.db_name = db_setup
    app.analytics_service.db_name = db_setup

    resp_officer = officer_client.get("/api/dashboard/summary?student_id=DASH1")
    data_officer = resp_officer.get_json()
    assert data_officer["average_stress_level"] is not None

    resp_tutor = tutor_client.get("/api/dashboard/summary?student_id=DASH1")
    data_tutor = resp_tutor.get_json()
    assert data_tutor["average_stress_level"] is None


def test_attendance_route(app, officer_client, db_setup):
    seed_core_student(db_setup, "ATT1")
    app.student_service.db_name = db_setup
    resp = officer_client.get("/attendance/ATT1")
    assert resp.status_code in (200, 302)


def test_officer_dashboard(app, officer_client, db_setup):
    seed_core_student(db_setup, "OFF1")
    app.student_service.db_name = db_setup
    resp = officer_client.get("/officer_dashboard")
    assert resp.status_code == 200


def test_stress_trend_api(app, officer_client, db_setup):
    seed_core_student(db_setup, "TREND1")
    app.analytics_service.db_name = db_setup
    data = officer_client.get("/api/chart/stress_trend").get_json()
    assert data["weeks"] == [1, 2]
    assert len(data["avg_stress"]) == 2


def test_attendance_vs_mark_api(app, officer_client, db_setup):
    seed_core_student(db_setup, "SCAT1")
    app.analytics_service.db_name = db_setup
    data = officer_client.get("/api/chart/attendance_vs_mark").get_json()
    assert len(data) >= 1
    assert {"module_id", "avg_attendance", "avg_mark"}.issubset(data[0].keys())


def test_feedback_summary_api(app, officer_client, db_setup):
    seed_core_student(db_setup, "FDB1")
    app.analytics_service.db_name = db_setup
    data = officer_client.get("/api/feedback/summary").get_json()
    assert "avg_pace_rating" in data
    assert data["avg_pace_rating"] > 0


def test_csv_import_validation(app, officer_client):
    bad_csv = "student_id,module_id,mark\nS1,1,bad\n"
    resp_bad = officer_client.post("/api/import/submissions", data=bad_csv)
    assert resp_bad.status_code == 400
    assert "Mark must be a number" in resp_bad.get_json()["message"]

    good_csv = "student_id,module_id,mark\nS1,1,70\n"
    resp_good = officer_client.post("/api/import/submissions", data=good_csv)
    assert resp_good.status_code == 200
    assert resp_good.get_json()["rows_processed"] == 1

