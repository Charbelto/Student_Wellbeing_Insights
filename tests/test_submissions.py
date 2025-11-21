import pytest
from datetime import datetime
from app.database.models import Submission

def test_submit_assignment(submission_service):
    student_id = 1
    assignment_id = "A1"
    submission_date = datetime.now()
    
    submission = submission_service.submit_assignment(student_id, assignment_id, submission_date)
    
    assert isinstance(submission, Submission)
    assert submission.student_id == student_id
    assert submission.assignment_id == assignment_id
    assert submission.grade is None

def test_grade_submission(submission_service):
    submission = submission_service.submit_assignment(1, "A1", datetime.now())
    updated_submission = submission_service.grade_submission(submission.id, 85.0)
    
    assert updated_submission.grade == 85.0

def test_get_student_submissions(submission_service):
    submission_service.submit_assignment(1, "A1", datetime.now())
    submission_service.submit_assignment(1, "A2", datetime.now())
    
    submissions = submission_service.get_student_submissions(1)
    assert len(submissions) == 2

