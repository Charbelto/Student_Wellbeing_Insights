import pytest

def test_home_page(auth_client):
    response = auth_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to officer dashboard if admin
    assert b"Wellbeing Officer Dashboard" in response.data or b"Welcome" in response.data

def test_dashboard_page(auth_client, student_service):
    s = student_service.create_student("u1", "Test Student")
    response = auth_client.get(f'/dashboard?student_id={s.id}')
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_submit_survey_api(auth_client, student_service):
    s = student_service.create_student("u1", "Test Student")
    data = {
        "student_id": s.id,
        "stress_level": 3,
        "hours_slept": 7.5,
        "comments": "Test comment"
    }
    response = auth_client.post('/api/submit-survey', json=data)
    assert response.status_code == 201
    assert response.json['status'] == 'success'
