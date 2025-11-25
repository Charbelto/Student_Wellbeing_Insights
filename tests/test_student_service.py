import pytest
from app.database.models import Student

def test_create_student(student_service):
    student = student_service.create_student("Alice Smith", "alice@example.com")
    assert isinstance(student, Student)
    assert student.id is not None
    assert student.name == "Alice Smith"
    assert student.email == "alice@example.com"

def test_get_student(student_service):
    created = student_service.create_student("Bob Jones", "bob@example.com")
    retrieved = student_service.get_student(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Bob Jones"

def test_get_all_students(student_service):
    student_service.create_student("S1", "s1@test.com")
    student_service.create_student("S2", "s2@test.com")
    students = student_service.get_all_students()
    assert len(students) >= 2

def test_create_duplicate_email(student_service):
    student_service.create_student("S1", "unique@test.com")
    with pytest.raises(ValueError):
        student_service.create_student("S2", "unique@test.com")

