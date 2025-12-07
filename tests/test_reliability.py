import sqlite3
import pytest
from app.database.connection import get_db_connection


def test_foreign_keys_prevent_orphan_submission(db_setup):
    conn = get_db_connection(db_setup)
    cur = conn.cursor()

    # Create degree and module so module FK passes
    cur.execute("INSERT INTO degrees(degree_name) VALUES('CS')")
    degree_id = cur.lastrowid
    cur.execute(
        "INSERT INTO modules(module_id, degree_id, code, name, semester, lecture_day, lecture_time) VALUES(1, ?, 'CS101', 'Intro', 1, 'Mon', '09:00')",
        (degree_id,),
    )
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            """
            INSERT INTO submissions(submission_id, student_id, module_id, semester, deadline_datetime, submitted_datetime, early_late_submissions, mark, late)
            VALUES(1, 'NO_STUDENT', 1, 1, '2023-10-10', '2023-10-11', 0, 70, 0)
            """
        )
        conn.commit()

    conn.close()

