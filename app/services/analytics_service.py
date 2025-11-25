from typing import List, Dict, Any
from app.database.connection import get_db_connection
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService

class AnalyticsService:
    def __init__(self, attendance_service: AttendanceService, wellbeing_service: WellbeingService, submission_service: SubmissionService, db_name='wellbeing.db'):
        self.attendance_service = attendance_service
        self.wellbeing_service = wellbeing_service
        self.submission_service = submission_service
        self.db_name = db_name

    def get_student_wellbeing_summary(self, student_id: int) -> Dict[str, Any]:
        # Using SQL aggregation for efficient analytics
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Average Attendance
        cursor.execute("""
            SELECT 
                (CAST(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 as attendance_pct
            FROM attendance 
            WHERE student_id = ?
        """, (student_id,))
        att_row = cursor.fetchone()
        attendance_pct = att_row['attendance_pct'] if att_row and att_row['attendance_pct'] is not None else 0.0
        
        # Wellbeing Averages
        cursor.execute("""
            SELECT 
                AVG(stress_level) as avg_stress,
                AVG(hours_slept) as avg_sleep
            FROM wellbeing_surveys
            WHERE student_id = ?
        """, (student_id,))
        wb_row = cursor.fetchone()
        avg_stress = wb_row['avg_stress'] if wb_row and wb_row['avg_stress'] is not None else 0.0
        avg_sleep = wb_row['avg_sleep'] if wb_row and wb_row['avg_sleep'] is not None else 0.0
        
        conn.close()
            
        return {
            "student_id": student_id,
            "average_attendance_pct": attendance_pct,
            "average_stress_level": avg_stress,
            "average_hours_slept": avg_sleep
        }

    def get_student_wellbeing_history(self, student_id: int, limit: int = 30) -> Dict[str, List[Any]]:
        """
        Fetches historical wellbeing data for charts (last N records).
        Returns a dictionary with lists for dates, stress_levels, and hours_slept.
        """
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, stress_level, hours_slept
            FROM wellbeing_surveys
            WHERE student_id = ?
            ORDER BY date ASC
            LIMIT ?
        """, (student_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "dates": [row['date'] for row in rows],
            "stress_levels": [row['stress_level'] for row in rows],
            "hours_slept": [row['hours_slept'] for row in rows]
        }

    def identify_high_stress_weeks(self, threshold: int = 4) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Complex query to find students with high stress
        cursor.execute("""
            SELECT 
                ws.student_id, 
                s.name as student_name,
                ws.date, 
                ws.stress_level, 
                ws.comments
            FROM wellbeing_surveys ws
            JOIN students s ON ws.student_id = s.id
            WHERE ws.stress_level >= ?
            ORDER BY ws.date DESC
        """, (threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "student_id": row['student_id'],
            "student_name": row['student_name'],
            "date": row['date'],
            "stress_level": row['stress_level'],
            "comments": row['comments']
        } for row in rows]
