import pytest

def test_student_list_empty(client):
    response = client.get('/students')
    assert response.status_code == 200
    assert b"Students" in response.data

def test_add_student(client):
    response = client.post('/students/add', data={
        'name': 'New Student',
        'email': 'new@student.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"New Student" in response.data

def test_add_student_duplicate_email(client):
    client.post('/students/add', data={'name': 'S1', 'email': 'dup@test.com'})
    response = client.post('/students/add', data={'name': 'S2', 'email': 'dup@test.com'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Error" in response.data or b"exists" in response.data

