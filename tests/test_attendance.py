import pytest
from datetime import date
from app.database.models import Attendance

def test_record_attendance(attendance_service):
    student_id = 1
    course_id = "CS101"
    status = "Present"
    d = date(2023, 10, 1)
    
    attendance = attendance_service.record_attendance(student_id, course_id, status, d)
    
    assert isinstance(attendance, Attendance)
    assert attendance.student_id == student_id
    assert attendance.status == status
    assert attendance.date == d

def test_get_student_attendance(attendance_service):
    student_id = 1
    attendance_service.record_attendance(student_id, "CS101", "Present", date(2023, 10, 1))
    attendance_service.record_attendance(student_id, "CS101", "Absent", date(2023, 10, 8))
    
    records = attendance_service.get_student_attendance(student_id)
    assert len(records) == 2
    assert records[0].status == "Present"
    assert records[1].status == "Absent"

def test_calculate_average_attendance(attendance_service):
    student_id = 1
    attendance_service.record_attendance(student_id, "CS101", "Present", date(2023, 10, 1))
    attendance_service.record_attendance(student_id, "CS101", "Present", date(2023, 10, 2))
    attendance_service.record_attendance(student_id, "CS101", "Absent", date(2023, 10, 3))
    
    avg = attendance_service.calculate_average_attendance(student_id)
    assert avg == pytest.approx(66.67, rel=0.01)

