import pytest
from app.database.models import Student

def test_create_student(student_service):
    # New signature: university_id, name, email...
    student = student_service.create_student("u123", "Alice Smith", "alice@example.com")
    assert isinstance(student, Student)
    assert student.id is not None
    assert student.name == "Alice Smith"
    assert student.email == "alice@example.com"

def test_get_student(student_service):
    created = student_service.create_student("u456", "Bob Jones", "bob@example.com")
    retrieved = student_service.get_student(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Bob Jones"

def test_get_all_students(student_service):
    student_service.create_student("u1", "S1", "s1@test.com")
    student_service.create_student("u2", "S2", "s2@test.com")
    students = student_service.get_all_students()
    assert len(students) >= 2

def test_create_duplicate_university_id(student_service):
    # Should return existing if duplicate
    s1 = student_service.create_student("uUnique", "S1")
    s2 = student_service.create_student("uUnique", "S2") # Should return s1
    assert s1.id == s2.id
