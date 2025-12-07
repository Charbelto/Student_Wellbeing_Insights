from datetime import datetime
import pytest
from app.database.connection import get_db_connection
from app.database.models import Submission


@pytest.fixture
def seeded_submission_env(db_setup):
    conn = get_db_connection(db_setup)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES(?,1,'CS',1,'18-21','UK')",
        ("SS1",),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", ("SS1", "Sub Student"))
    cur.execute(
        "INSERT INTO modules(module_id, degree_id, code, name, semester, lecture_day, lecture_time) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (1, 1, "CS101", "Intro CS", 1, "Mon", "09:00"),
    )
    conn.commit()
    conn.close()
    return ("SS1", 1)


def test_submit_and_grade_submission(submission_service, seeded_submission_env):
    student_id, module_id = seeded_submission_env
    submission = submission_service.submit_assignment(
        submission_id=1,
        student_id=student_id,
        module_id=module_id,
        semester=1,
        deadline_datetime=datetime(2023, 10, 10, 12, 0),
        submitted_datetime=datetime(2023, 10, 11, 12, 0),
        early_late_submissions=1,
        mark=None,
        late=True,
    )
    assert isinstance(submission, Submission)
    assert submission.student_id == student_id
    updated = submission_service.grade_submission(submission.submission_id, 85.0)
    assert updated.mark == 85.0


def test_get_and_delete_submissions(submission_service, seeded_submission_env):
    student_id, module_id = seeded_submission_env
    s1 = submission_service.submit_assignment(
        1, student_id, module_id, 1,
        datetime(2023, 10, 10, 12, 0),
        datetime(2023, 10, 11, 12, 0),
        1, True, None
    )
    submissions = submission_service.get_student_submissions(student_id)
    assert len(submissions) == 1
    assert submissions[0].submission_id == s1.submission_id
    assert submission_service.delete_submission(s1.submission_id) is True
    assert submission_service.get_student_submissions(student_id) == []
