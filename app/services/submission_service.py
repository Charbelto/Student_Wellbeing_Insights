from typing import List
from datetime import datetime
from app.database.models import Submission

class SubmissionService:
    def __init__(self):
        self._storage = []

    def submit_assignment(self, student_id: int, assignment_id: str, submission_date: datetime) -> Submission:
        raise NotImplementedError

    def grade_submission(self, submission_id: int, grade: float) -> Submission:
        raise NotImplementedError

    def get_student_submissions(self, student_id: int) -> List[Submission]:
        raise NotImplementedError

