from typing import List
from datetime import date, datetime
from app.database.models import Attendance
from app.database.connection import get_db_connection
import app.database.queries as q


def _ensure_iso_date(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise ValueError("date must be a date, datetime, or ISO string")


class AttendanceService:
    def __init__(self, db_name: str = 'wellbeing.db'):
        self.db_name = db_name

    def record_attendance(self, student_id: int, course_id: str, status: str, record_date) -> Attendance:
        date_str = _ensure_iso_date(record_date)
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.INSERT_ATTENDANCE, (student_id, course_id, status, date_str))
        conn.commit()
        record_id = cursor.lastrowid
        cursor.execute(q.GET_ATTENDANCE_BY_ID, (record_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_attendance(row)

    def get_student_attendance(self, student_id: int) -> List[Attendance]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT, (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_attendance(row) for row in rows]

    def calculate_average_attendance(self, student_id: int) -> float:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.COUNT_ATTENDANCE_SUMMARY, (student_id,))
        row = cursor.fetchone()
        conn.close()
        if not row or row["total_count"] == 0:
            return 0.0
        percentage = (row["present_count"] / row["total_count"]) * 100
        return round(percentage, 2)

    def update_attendance(self, record_id: int, status: str) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.UPDATE_ATTENDANCE_STATUS, (status, record_id))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Attendance record with id {record_id} not found")
        conn.commit()
        cursor.execute(q.GET_ATTENDANCE_BY_ID, (record_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_attendance(row)

    def delete_attendance(self, record_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.DELETE_ATTENDANCE, (record_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Attendance record with id {record_id} not found")
        conn.commit()
        conn.close()
        return True

    def _row_to_attendance(self, row) -> Attendance:
        return Attendance(
            id=row["id"],
            student_id=row["student_id"],
            course_id=row["course_id"],
            status=row["status"],
            date=date.fromisoformat(row["date"]),
        )
