from datetime import datetime
import pytest
from app.database.connection import get_db_connection


@pytest.fixture
def seeded_attendance(db_setup):
    conn = get_db_connection(db_setup)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES(?,1,'CS',1,'18-21','UK')",
        ("S-A1",),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", ("S-A1", "Att Student"))
    cur.execute(
        "INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate) VALUES(?, ?, ?, ?, ?)",
        ("S-A1", 1, 0, 0, 0.0),
    )
    conn.commit()
    conn.close()
    return "S-A1"


def test_record_attendance_increments(attendance_service, seeded_attendance):
    rec = attendance_service.record_attendance(seeded_attendance, 1)
    assert rec.attended_sessions == 1
    assert rec.total_sessions == 1
    assert rec.attendance_rate == pytest.approx(1.0)


def test_record_absence_increments_total(attendance_service, seeded_attendance):
    rec = attendance_service.record_absence(seeded_attendance, 1)
    assert rec.attended_sessions == 0
    assert rec.total_sessions == 1
    assert rec.attendance_rate == pytest.approx(0.0)


def test_get_attendance_rate(attendance_service, seeded_attendance):
    attendance_service.record_attendance(seeded_attendance, 1)
    rate = attendance_service.get_attendance_rate(seeded_attendance)
    assert rate == pytest.approx(1.0)
