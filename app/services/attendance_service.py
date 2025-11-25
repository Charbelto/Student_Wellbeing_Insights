from typing import List, Optional
from datetime import date
from app.database.models import Attendance
from app.database.connection import get_db_connection

class AttendanceService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def record_attendance(self, student_id: int, course_id: str, status: str, date: date) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (student_id, course_id, status, date) VALUES (?, ?, ?, ?)",
            (student_id, course_id, status, date)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return Attendance(
            id=record_id,
            student_id=student_id,
            course_id=course_id,
            status=status,
            date=date
        )

    def get_student_attendance(self, student_id: int) -> List[Attendance]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [Attendance(
            id=row['id'],
            student_id=row['student_id'],
            course_id=row['course_id'],
            status=row['status'],
            date=row['date']
        ) for row in rows]

    def calculate_average_attendance(self, student_id: int) -> float:
        records = self.get_student_attendance(student_id)
        if not records:
            return 0.0
        
        present_count = sum(1 for r in records if r.status == "Present")
        return (present_count / len(records)) * 100

    def update_attendance(self, attendance_id: int, status: str) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Check existence
        cursor.execute("SELECT * FROM attendance WHERE id = ?", (attendance_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Attendance record with id {attendance_id} not found")
            
        cursor.execute("UPDATE attendance SET status = ? WHERE id = ?", (status, attendance_id))
        conn.commit()
        conn.close()
        
        # Fetch updated to return complete object
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE id = ?", (attendance_id,))
        row = cursor.fetchone()
        conn.close()
        
        return Attendance(
            id=row['id'],
            student_id=row['student_id'],
            course_id=row['course_id'],
            status=row['status'],
            date=row['date']
        )

    def delete_attendance(self, attendance_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM attendance WHERE id = ?", (attendance_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Attendance record with id {attendance_id} not found")
            
        cursor.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
        conn.commit()
        conn.close()
        return True
