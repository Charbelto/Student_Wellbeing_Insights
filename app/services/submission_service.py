from typing import List
from datetime import datetime
from app.database.models import Submission
from app.database.connection import get_db_connection

class SubmissionService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def submit_assignment(self, student_id: int, assignment_id: str, submission_date: datetime) -> Submission:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO submissions (student_id, assignment_id, submission_date, grade) VALUES (?, ?, ?, ?)",
            (student_id, assignment_id, submission_date, None)
        )
        conn.commit()
        submission_id = cursor.lastrowid
        conn.close()
        
        return Submission(
            id=submission_id,
            student_id=student_id,
            assignment_id=assignment_id,
            submission_date=submission_date,
            grade=None
        )

    def grade_submission(self, submission_id: int, grade: float) -> Submission:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Submission with id {submission_id} not found")
            
        cursor.execute("UPDATE submissions SET grade = ? WHERE id = ?", (grade, submission_id))
        conn.commit()
        conn.close()
        
        # Fetch updated
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
        row = cursor.fetchone()
        conn.close()
        
        return Submission(
            id=row['id'],
            student_id=row['student_id'],
            assignment_id=row['assignment_id'],
            submission_date=row['submission_date'],
            grade=row['grade']
        )

    def get_student_submissions(self, student_id: int) -> List[Submission]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions WHERE student_id = ?", (student_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [Submission(
            id=row['id'],
            student_id=row['student_id'],
            assignment_id=row['assignment_id'],
            submission_date=row['submission_date'], # Datetime handling might need adjustment for string
            grade=row['grade']
        ) for row in rows]

    def delete_submission(self, submission_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM submissions WHERE id = ?", (submission_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Submission with id {submission_id} not found")
            
        cursor.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
        conn.commit()
        conn.close()
        return True
