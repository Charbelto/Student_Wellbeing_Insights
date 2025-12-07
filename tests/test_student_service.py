from app.database.models import Student


def test_create_and_get_student(student_service):
    student = student_service.create_student("Alice", "S123")
    assert isinstance(student, Student)
    fetched = student_service.get_student("S123")
    assert fetched is not None
    assert fetched.student_id == "S123"
    assert fetched.name == "Alice"


def test_get_all_students(student_service):
    student_service.create_student("S1 Name", "S1")
    student_service.create_student("S2 Name", "S2")
    students = student_service.get_all_students()
    ids = {s.student_id for s in students}
    assert {"S1", "S2"}.issubset(ids)
