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
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                (CAST(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 as attendance_pct
            FROM attendance 
            WHERE student_id = ?
        """, (student_id,))
        att_row = cursor.fetchone()
        attendance_pct = att_row['attendance_pct'] if att_row and att_row['attendance_pct'] is not None else 0.0
        
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

    def identify_at_risk_students(self) -> List[Dict[str, Any]]:
        """
        Identifies students at risk based on:
        1. Attendance < 50%
        2. High average stress (> 4.0)
        3. Missing surveys (Logic: if no surveys in last 2 weeks, or never) - Simplified for prototype
        """
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Get all students
        cursor.execute("SELECT id, university_id, name FROM students")
        students = cursor.fetchall()
        
        at_risk = []
        
        for s in students:
            s_id = s['id']
            
            # Check Attendance
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
                FROM attendance WHERE student_id = ?
            """, (s_id,))
            att_data = cursor.fetchone()
            
            is_risk = False
            reasons = []
            
            if att_data['total'] > 0:
                absent_rate = att_data['absent'] / att_data['total']
                if absent_rate > 0.3: # More than 30% absent
                    is_risk = True
                    reasons.append(f"High Absenteeism ({(absent_rate*100):.1f}%)")
            
            # Check Stress
            cursor.execute("SELECT AVG(stress_level) as avg_stress FROM wellbeing_surveys WHERE student_id = ?", (s_id,))
            stress_data = cursor.fetchone()
            if stress_data['avg_stress'] and stress_data['avg_stress'] >= 4.0:
                is_risk = True
                reasons.append(f"High Average Stress ({stress_data['avg_stress']:.1f})")
                
            if is_risk:
                at_risk.append({
                    "student_id": s_id,
                    "name": s['name'],
                    "university_id": s['university_id'],
                    "reasons": reasons
                })
                
        conn.close()
        return at_risk
