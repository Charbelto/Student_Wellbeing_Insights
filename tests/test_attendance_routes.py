import pytest
from datetime import date

def test_attendance_page(client, student_service):
    # Setup student
    s = student_service.create_student("Att Student", "att@test.com")
    response = client.get(f'/attendance/{s.id}')
    assert response.status_code == 200
    assert b"Attendance Records" in response.data

def test_add_attendance_route(client, student_service):
    s = student_service.create_student("Att Student 2", "att2@test.com")
    
    response = client.post('/attendance/add', data={
        'student_id': s.id,
        'course_id': 'CS101',
        'status': 'Present',
        'date': '2023-10-01'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Present" in response.data
    assert b"CS101" in response.data

def test_delete_attendance_route(client, student_service, attendance_service):
    s = student_service.create_student("Att Student 3", "att3@test.com")
    att = attendance_service.record_attendance(s.id, "CS101", "Absent", date.today())
    
    response = client.post(f'/attendance/delete/{att.id}?student_id={s.id}', follow_redirects=True)
    
    assert response.status_code == 200
    # Should verify absence of the record or success message
    # For now, just checking page load OK

