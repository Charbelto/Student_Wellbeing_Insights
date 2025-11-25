import pytest
from datetime import datetime

def test_submission_page(auth_client, student_service):
    s = student_service.create_student("u1", "Sub Student", "sub@test.com")
    response = auth_client.get(f'/submissions/{s.id}')
    assert response.status_code == 200
    assert b"Assignment" in response.data

def test_add_submission_route(auth_client, student_service):
    s = student_service.create_student("u2", "Sub Student 2", "sub2@test.com")
    
    response = auth_client.post('/submissions/add', data={
        'student_id': s.id,
        'assignment_id': 'A1',
        'submission_date': '2023-10-01T12:00:00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"A1" in response.data

def test_grade_submission_route(auth_client, student_service, submission_service):
    s = student_service.create_student("u3", "Sub Student 3", "sub3@test.com")
    sub = submission_service.submit_assignment(s.id, "A2", datetime.now())
    
    response = auth_client.post(f'/submissions/grade/{sub.id}?student_id={s.id}', data={
        'grade': '85.5'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"85.5" in response.data

def test_delete_submission_route(auth_client, student_service, submission_service):
    s = student_service.create_student("u4", "Sub Student 4", "sub4@test.com")
    sub = submission_service.submit_assignment(s.id, "A3", datetime.now())
    
    response = auth_client.post(f'/submissions/delete/{sub.id}?student_id={s.id}', follow_redirects=True)
    
    assert response.status_code == 200
    # Check deletion effectively happened if we query service, but checking HTTP ok for now
    assert len(submission_service.get_student_submissions(s.id)) == 0
