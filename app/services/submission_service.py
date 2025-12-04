from typing import List
from datetime import datetime
from app.database.models import Submission
from app.database.connection import get_db_connection
import app.database.queries as q

class SubmissionService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def submit_assignment(self, submission_id: int,
                        student_id: str,
                        module_id: int,
                        semester: int,
                        deadline_datetime: datetime,
                        submitted_datetime: datetime,
                        early_late_submissions: int,
                        late: bool,
                        mark: float = None) -> Submission:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(q.INSERT_SUBMISSION,
            (submission_id,
            student_id,
            module_id,
            semester,
            deadline_datetime,
            submitted_datetime,
            early_late_submissions,
            mark,
            late)
        )
        conn.commit()
        submission_id = cursor.lastrowid
        conn.close()
        
        return Submission(
            submission_id=submission_id,
            student_id=student_id,
            module_id=module_id,
            semester=semester,
            deadline_datetime=deadline_datetime,
            submitted_datetime=submitted_datetime,
            early_late_submissions=early_late_submissions,
            mark=mark,
            late=late
        )

    def grade_submission(self, submission_id: int, mark: float) -> Submission:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(q.GET_SUBMISSION, (submission_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Submission with id {submission_id} not found")
            
        cursor.execute(q.UPDATE_MARK, (mark, submission_id))
        conn.commit()
        conn.close()
        
        # Fetch updated
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_SUBMISSION, (submission_id,))
        row = cursor.fetchone()
        conn.close()
        
        return Submission(
            submission_id=row['submission_id'],
            student_id=row['student_id'],
            module_id=row['module_id'],
            semester=row['semester'],
            deadline_datetime=row['deadline_datetime'],
            submitted_datetime=row['submitted_datetime'],
            early_late_submissions=row['early_late_submissions'],
            mark=row['mark'],
            late=row['late']
        )

    def get_student_submissions(self, student_id: str) -> List[Submission]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_SUBMISSIONS_FOR_STUDENT, (student_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [Submission(
            submission_id=row['submission_id'],
            student_id=row['student_id'],
            module_id=row['module_id'],
            semester=row['semester'],
            deadline_datetime=row['deadline_datetime'],
            submitted_datetime=row['submitted_datetime'],
            early_late_submissions=row['early_late_submissions'],
            mark=row['mark'],
            late=row['late']
        ) for row in rows]

    def delete_submission(self, submission_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute(q.GET_SUBMISSION, (submission_id,))
            if not cursor.fetchone():
                raise ValueError(f"Submission with id {submission_id} not found")
                
            cursor.execute(q.DELETE_SUBMISSION, (submission_id,))
            conn.commit()
            return True
        finally:
            conn.close()
