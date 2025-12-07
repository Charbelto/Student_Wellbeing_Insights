import io
import csv
import pytest
from app.database.connection import get_db_connection
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("viz_officer", "pass", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "viz_officer", "password": "pass"}, follow_redirects=True)
    return c


def seed_visual_data(db_name: str):
    """Seed enough data to generate stress trend and attendance vs mark plots."""
    conn = get_db_connection(db_name)
    cur = conn.cursor()

    # Degree + module
    cur.execute("INSERT INTO degrees(degree_name) VALUES('Computing')")
    degree_id = cur.lastrowid
    cur.execute(
        "INSERT INTO modules(module_id, degree_id, code, name, semester, lecture_day, lecture_time) VALUES(1, ?, 'CS101', 'Intro CS', 1, 'Mon', '09:00')",
        (degree_id,),
    )

    # Student and name
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES('VIZ1', ?, 'Computing', 1, '18-21', 'UK')",
        (degree_id,),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES('VIZ1', 'Viz Student')")

    # Attendance + submissions for scatter
    cur.execute(
        "INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate) VALUES('VIZ1', 1, 10, 8, 0.8)"
    )
    cur.execute(
        "INSERT INTO submissions(submission_id, student_id, module_id, semester, deadline_datetime, submitted_datetime, early_late_submissions, mark, late) VALUES(1,'VIZ1',1,1,'2023-10-10','2023-10-11',0,75,0)"
    )

    # Stress surveys for line graph
    for week, stress in enumerate([2, 3, 4, 5], start=1):
        cur.execute(
            "INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES('VIZ1', ?, ?, 7, 3)",
            (week, stress),
        )

    conn.commit()
    conn.close()


def test_stress_trend_png(officer_client, db_setup, app):
    seed_visual_data(db_setup)
    app.analytics_service.db_name = db_setup

    resp = officer_client.get("/visualizations/stress_trend.png")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("image/png")
    assert len(resp.data) > 500  # some bytes returned


def test_attendance_vs_mark_png(officer_client, db_setup, app):
    seed_visual_data(db_setup)
    app.analytics_service.db_name = db_setup

    resp = officer_client.get("/visualizations/attendance_vs_mark.png")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("image/png")
    assert len(resp.data) > 500

