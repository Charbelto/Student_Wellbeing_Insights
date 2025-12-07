import pytest
from app.database.connection import get_db_connection

def test_student_wellbeing_summary(analytics_service, db_setup):
    conn = get_db_connection(db_setup)
    cur = conn.cursor()
    cur.execute("INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES(?,1,'CS',1,'18-21','UK')", ("AN1",))
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", ("AN1", "Ana Lytics"))
    cur.execute("INSERT INTO attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate) VALUES(?, ?, ?, ?, ?)", ("AN1", 1, 10, 7, 0.7))
    cur.execute("INSERT INTO survey(student_id, week, stress_level, hours_slept, mood_score) VALUES(?, ?, ?, ?, ?)", ("AN1", 1, 4, 6, 3))
    conn.commit()
    conn.close()

    summary = analytics_service.get_student_wellbeing_summary("AN1")
    assert summary["student_id"] == "AN1"
    assert summary["average_attendance_rate"] == pytest.approx(0.7)
    assert summary["average_stress_level"] == pytest.approx(4.0)