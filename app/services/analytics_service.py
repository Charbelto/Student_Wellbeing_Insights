from typing import List, Dict, Any
from app.database.connection import get_db_connection
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService
import app.database.queries as q

class AnalyticsService:
    def __init__(self, attendance_service: AttendanceService, wellbeing_service: WellbeingService, submission_service: SubmissionService, db_name='wellbeing.db'):
        self.attendance_service = attendance_service
        self.wellbeing_service = wellbeing_service
        self.submission_service = submission_service
        self.db_name = db_name

    def get_student_wellbeing_summary(self, student_id: str) -> Dict[str, Any]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(q.GET_ATTENDANCE_RATE_FOR_STUDENT, (student_id,))
        att_row = cursor.fetchone()
        attendance_rate = att_row['attendance_rate'] if att_row and att_row['attendance_rate'] is not None else 0.0
        
        cursor.execute(q.AVG_WELLBEING_STATS, (student_id,))
        wb_row = cursor.fetchone()
        avg_stress = wb_row['avg_stress'] if wb_row and wb_row['avg_stress'] is not None else 0.0
        avg_sleep = wb_row['avg_sleep'] if wb_row and wb_row['avg_sleep'] is not None else 0.0
        avg_mood = wb_row['avg_mood'] if wb_row and wb_row['avg_mood'] is not None else 0.0


        conn.close()
            
        return {
            "student_id": student_id,
            "average_attendance_rate": attendance_rate,
            "average_stress_level": avg_stress,
            "average_hours_slept": avg_sleep,
            "average_mood": avg_mood
        }

    def get_student_wellbeing_history(self, student_id: str, limit: int = 30) -> Dict[str, List[Any]]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(q.GET_WELLBEING_FOR_STUDENT, (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "week": [row['week'] for row in rows],
            "stress_levels": [row['stress_level'] for row in rows],
            "hours_slept": [row['hours_slept'] for row in rows],
            "mood_score": [row['mood_score'] for row in rows]

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
        cursor.execute(q.GET_ALL_STUDENTS_AND_NAME)
        students = cursor.fetchall()
        
        at_risk = []
        
        for s in students:
            s_id = s['student_id']
            
            # Check Attendance
            cursor.execute(q.GET_ATTENDANCE_RATE_FOR_STUDENT, (s_id,))
            att_data = cursor.fetchone()
            
            is_risk = False
            reasons = []
            
            if att_data['total'] > 0:
                absent_rate = 100 - att_data['attendance_rate']
                if absent_rate > 0.3: # More than 30% absent
                    is_risk = True
                    reasons.append(f"High Absenteeism ({(absent_rate*100):.1f}%)")
            
            # Check Stress
            cursor.execute(q.AVG_STRESS_STAT, (s_id,))
            stress_data = cursor.fetchone()
            if stress_data['avg_stress'] and stress_data['avg_stress'] >= 4.0:
                is_risk = True
                reasons.append(f"High Average Stress ({stress_data['avg_stress']:.1f})")
                
            if is_risk:
                at_risk.append({
                    "student_id": s_id,
                    "name": s['name'],
                    "absence rate": absent_rate,
                    "average stress": stress_data['avg_stress'],
                    "reasons": reasons
                })
                
        conn.close()
        return at_risk
