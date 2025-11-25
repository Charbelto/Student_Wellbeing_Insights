import pytest

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Student Wellbeing" in response.data

def test_dashboard_page(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    # Should probably show some stats
    assert b"Attendance" in response.data
    assert b"Stress" in response.data

def test_submit_survey_api(client):
    data = {
        "student_id": 1,
        "stress_level": 3,
        "hours_slept": 7.5,
        "comments": "Test comment"
    }
    response = client.post('/api/submit-survey', json=data)
    assert response.status_code == 201
    assert response.json['status'] == 'success'

