from typing import List, Optional
from datetime import date
from app.database.models import Attendance

class AttendanceService:
    def __init__(self):
        self._storage: List[Attendance] = [] 

    def record_attendance(self, student_id: int, course_id: str, status: str, date: date) -> Attendance:
        record = Attendance(
            student_id=student_id,
            course_id=course_id,
            status=status,
            date=date,
            id=len(self._storage) + 1
        )
        self._storage.append(record)
        return record

    def get_student_attendance(self, student_id: int) -> List[Attendance]:
        return [r for r in self._storage if r.student_id == student_id]

    def calculate_average_attendance(self, student_id: int) -> float:
        records = self.get_student_attendance(student_id)
        if not records:
            return 0.0
        
        present_count = sum(1 for r in records if r.status == "Present")
        return (present_count / len(records)) * 100
