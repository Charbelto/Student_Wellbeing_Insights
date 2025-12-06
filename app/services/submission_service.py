from typing import List
from datetime import datetime
from app.database.models import Submission
from app.database.connection import get_db_connection
import app.database.queries as q


def _ensure_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError("submission_date must be a datetime or ISO string")


class SubmissionService:
    def __init__(self, db_name: str = 'wellbeing.db'):
        self.db_name = db_name

    def submit_assignment(self, student_id: int, assignment_id: str, submission_date) -> Submission:
        dt = _ensure_datetime(submission_date)
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.INSERT_SUBMISSION, (student_id, assignment_id, dt.isoformat(), None))
        conn.commit()
        submission_id = cursor.lastrowid
        cursor.execute(q.GET_SUBMISSION, (submission_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_submission(row)

    def grade_submission(self, submission_id: int, grade: float) -> Submission:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.UPDATE_SUBMISSION_GRADE, (grade, submission_id))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Submission with id {submission_id} not found")
        conn.commit()
        cursor.execute(q.GET_SUBMISSION, (submission_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_submission(row)

    def get_student_submissions(self, student_id: int) -> List[Submission]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_SUBMISSIONS_FOR_STUDENT, (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_submission(row) for row in rows]

    def delete_submission(self, submission_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.DELETE_SUBMISSION, (submission_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Submission with id {submission_id} not found")
        conn.commit()
        conn.close()
        return True

    def _row_to_submission(self, row) -> Submission:
        return Submission(
            id=row["id"],
            student_id=row["student_id"],
            assignment_id=row["assignment_id"],
            submission_date=datetime.fromisoformat(row["submission_date"]),
            grade=row["grade"],
        )
