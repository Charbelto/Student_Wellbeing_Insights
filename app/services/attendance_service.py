from typing import List, Optional
from datetime import date
from app.database.models import Attendance
from app.database.connection import get_db_connection
import app.database.queries as q

class AttendanceService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def record_attendance(self, student_id: str, module_id: str) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(q.UPDATE_ATTENDANCE_PRESENT, (student_id, module_id))
        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT_AND_MODULE, (student_id, module_id))
        row = cursor.fetchone()

        conn.commit()
        conn.close()
        
        return Attendance(
            student_id=row["student_id"],
            module_id=row["module_id"],
            total_sessions=row["total_sessions"],
            attended_sessions=row["attended_sessions"],
            attendance_rate=row["attendance_rate"]
        )
    
    def record_absence(self, student_id: str, module_id: str) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(q.UPDATE_ATTENDANCE_ABSENT, (student_id, module_id))
        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT_AND_MODULE, (student_id, module_id))
        row = cursor.fetchone()

        conn.commit()
        conn.close()
        
        return Attendance(
            student_id=row["student_id"],
            module_id=row["module_id"],
            total_sessions=row["total_sessions"],
            attended_sessions=row["attended_sessions"],
            attendance_rate=row["attendance_rate"]
        )

    def get_student_attendance(self, student_id: str) -> List[Attendance]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT, (student_id,))
        rows = cursor.fetchall()

        conn.close()
        
        return [Attendance(
            student_id=row["student_id"],
            module_id=row["module_id"],
            total_sessions=row["total_sessions"],
            attended_sessions=row["attended_sessions"],
            attendance_rate=row["attendance_rate"]
        ) for row in rows]

    def get_attendance_rate(self, student_id: str):
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(q.GET_ATTENDANCE_RATE_FOR_STUDENT, (student_id,))
        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None   # student not found

        return row["attendance_rate"]

    def update_attendance(self, student_id: str, module_id: int, total_sessions: int, attended_sessions: int, attendance_rate: float) -> Attendance:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Check existence
        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT_AND_MODULE, (student_id, module_id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(
                    f"Attendance record with student id {student_id} and module id {module_id} not found"
            )
            
        cursor.execute(q.UPDATE_ATTENDANCE, (student_id, module_id, total_sessions, attended_sessions, attendance_rate))
        conn.commit()
        conn.close()
        
        # Fetch updated to return complete object
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT_AND_MODULE, (student_id, module_id))
        row = cursor.fetchone()
        conn.close()
        
        return Attendance(
            id=row['id'],
            student_id=row['student_id'],
            module_id=row['module_id'],
            status=row['status'],
            date=row['date']
        )

    def delete_attendance(self, student_id: str, module_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(q.GET_ATTENDANCE_FOR_STUDENT_AND_MODULE, (student_id, module_id))
            row = cursor.fetchone()

            if row is None:
                raise ValueError(
                    f"Attendance record with student id {student_id} and module id {module_id} not found"
                )

            cursor.execute(q.DELETE_MODULE_STUDENT_ATTENDANCE, (student_id, module_id))
            conn.commit()
            return True

        finally:
            conn.close()
