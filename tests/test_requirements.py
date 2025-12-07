import csv
import io
import pytest
from flask import url_for
from app.database.connection import get_db_connection
from app.database.models import Role


@pytest.fixture
def officer_client(app, user_service):
    user_service.create_user("officer", "admin123", Role.WELLBEING_OFFICER)
    c = app.test_client()
    c.post("/login", data={"username": "officer", "password": "admin123"}, follow_redirects=True)
    return c


@pytest.fixture
def tutor_client(app, user_service):
    user_service.create_user("tutor", "tutor123", Role.TUTOR)
    c = app.test_client()
    c.post("/login", data={"username": "tutor", "password": "tutor123"}, follow_redirects=True)
    return c


def seed_student_with_data(db_name: str, student_id: str = "S1", stress_levels=(4, 5), late_submissions=3):
    """Seed a student with survey and submission data."""
    conn = get_db_connection(db_name)
    cur = conn.cursor()
    # Ensure module exists for FK
    cur.execute(
        "INSERT OR IGNORE INTO modules(module_id, degree_id, code, name, semester, lecture_day, lecture_time) VALUES(1, 1, 'CS101', 'Intro CS', 1, 'Mon', '09:00')"
    )
    cur.execute(
        """
        INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile, medical_information, disabilities)
        VALUES(?, 1, 'CS', 1, '18-21', 'UK', 'asthma', 'none')
        """,
        (student_id,),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", (student_id, "Test User"))
    # Attendance baseline
    cur.execute(
        """
        INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate)
        VALUES(?, 1, 10, 7, 0.7)
        """,
        (student_id,),
    )
    # Surveys
    for week, stress in enumerate(stress_levels, start=1):
        cur.execute(
            "INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES(?, ?, ?, 6, 3)",
            (student_id, week, stress),
        )
    # Submissions
    for i in range(late_submissions):
        cur.execute(
            """
            INSERT INTO submissions(submission_id, student_id, module_id, semester, deadline_datetime, submitted_datetime,
                                    early_late_submissions, mark, late)
            VALUES(?, ?, 1, 1, '2023-10-10', '2023-10-11', 1, 60, 1)
            """,
            (i + 1, student_id),
        )
    conn.commit()
    conn.close()


def test_risk_flagging_matches_rules(analytics_service, db_setup):
    seed_student_with_data(db_setup, "S1", stress_levels=(5, 4), late_submissions=3)
    seed_student_with_data(db_setup, "S2", stress_levels=(2, 2), late_submissions=0)

    risks = analytics_service.identify_at_risk_students()
    risky_ids = {r["student_id"] for r in risks}

    assert "S1" in risky_ids
    assert "S2" not in risky_ids
    high_risk = next(r for r in risks if r["student_id"] == "S1")
    assert any("avg_stress" in reason.lower() or "late submissions" in reason.lower() for reason in high_risk["reasons"])


def test_export_risk_csv_privacy(officer_client, db_setup, analytics_service):
    seed_student_with_data(db_setup, "S1", stress_levels=(5, 5), late_submissions=3)
    # Force recompute risk list before export
    risks = analytics_service.identify_at_risk_students()
    assert risks

    resp = officer_client.get("/export/risk")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["Content-Type"]
    content = resp.data.decode()
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    assert rows
    assert set(rows[0].keys()) == {"student_id", "risk_reason"}
    assert "medical" not in content.lower()


def test_gdpr_delete_cascades(officer_client, db_setup, student_service):
    seed_student_with_data(db_setup, "S99", stress_levels=(5,), late_submissions=1)
    # Delete student
    student_service.delete_student("S99")
    conn = get_db_connection(db_setup)
    cur = conn.cursor()
    for table in ["students", "student_names", "attendance", "survey", "submissions", "risk_indicator"]:
        cur.execute(f"SELECT COUNT(*) AS c FROM {table} WHERE student_id = 'S99'")
        assert cur.fetchone()["c"] == 0
    conn.close()


def test_rbac_hides_medical_for_tutor(officer_client, tutor_client, db_setup, student_service):
    seed_student_with_data(db_setup, "S3", stress_levels=(3,), late_submissions=0)
    # Officer can see medical info
    resp_officer = officer_client.get("/api/students")
    assert resp_officer.status_code == 200
    assert any(s.get("medical_information") for s in resp_officer.get_json())
    # Tutor should see redacted values
    resp_tutor = tutor_client.get("/api/students")
    assert resp_tutor.status_code == 200
    assert all(s.get("medical_information") is None for s in resp_tutor.get_json())


def test_passwords_are_bcrypt_hashed(user_service):
    user = user_service.create_user("secure", "strongpass", Role.WELLBEING_OFFICER)
    assert user.password_hash != "strongpass"
    assert user.password_hash.startswith("$2b$")

