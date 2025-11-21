from typing import List, Optional
from datetime import date
from app.database.models import Attendance

class AttendanceService:
    def __init__(self):
        self._storage = [] 

    def record_attendance(self, student_id: int, course_id: str, status: str, date: date) -> Attendance:
        raise NotImplementedError

    def get_student_attendance(self, student_id: int) -> List[Attendance]:
        raise NotImplementedError

    def calculate_average_attendance(self, student_id: int) -> float:
        raise NotImplementedError

