from typing import List
from datetime import datetime
from app.database.models import Submission

class SubmissionService:
    def __init__(self):
        self._storage: List[Submission] = []

    def submit_assignment(self, student_id: int, assignment_id: str, submission_date: datetime) -> Submission:
        submission = Submission(
            student_id=student_id,
            assignment_id=assignment_id,
            submission_date=submission_date,
            id=len(self._storage) + 1
        )
        self._storage.append(submission)
        return submission

    def grade_submission(self, submission_id: int, grade: float) -> Submission:
        for submission in self._storage:
            if submission.id == submission_id:
                submission.grade = grade
                return submission
        raise ValueError(f"Submission with id {submission_id} not found")

    def get_student_submissions(self, student_id: int) -> List[Submission]:
        return [s for s in self._storage if s.student_id == student_id]
