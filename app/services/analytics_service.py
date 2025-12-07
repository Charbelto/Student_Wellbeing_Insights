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

    def get_stress_trend(self) -> Dict[str, List[Any]]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.STRESS_TREND_AVG)
        rows = cursor.fetchall()
        conn.close()
        return {
            "weeks": [row["week"] for row in rows],
            "avg_stress": [row["avg_stress"] for row in rows],
        }

    def get_attendance_vs_mark(self) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.ATTENDANCE_VS_MARKS)
        rows = cursor.fetchall()
        conn.close()
        return [
            {"module_id": row["module_id"], "avg_attendance": row["avg_attendance"], "avg_mark": row["avg_mark"]}
            for row in rows
        ]

    def get_feedback_summary(self) -> Dict[str, Any]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.FEEDBACK_PACE_AVG)
        row = cursor.fetchone()
        conn.close()
        return {"avg_pace_rating": row["avg_pace"] if row and row["avg_pace"] is not None else 0}

    def identify_at_risk_students(self) -> List[Dict[str, Any]]:
        """
        Identifies students at risk based on:
        - Explicit risk_level of "High" in risk_indicator table
        - Average stress >= 4.0
        - Late submissions > 2
        """
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Get all students
        cursor.execute(q.GET_ALL_STUDENTS_AND_NAME)
        students = cursor.fetchall()
        
        at_risk = []
        
        for s in students:
            s_id = s['student_id']
            
            is_risk = False
            reasons = []

            # Risk table explicit flag
            cursor.execute(q.GET_RISK, (s_id,))
            risk_row = cursor.fetchone()
            if risk_row and risk_row['risk_level'] == 'High':
                is_risk = True
                reasons.append("risk_level=High")

            # Average stress
            cursor.execute(q.AVG_STRESS_STAT, (s_id,))
            stress_data = cursor.fetchone()
            avg_stress = stress_data['avg_stress'] if stress_data and stress_data['avg_stress'] is not None else 0
            if avg_stress >= 4.0:
                is_risk = True
                reasons.append(f"avg_stress {avg_stress:.1f} >= 4.0")

            # Late submissions
            cursor.execute(q.LATE_SUBMISSION_COUNT, (s_id,))
            late_data = cursor.fetchone()
            late_count = late_data['late_submissions'] if late_data else 0
            if late_count > 2:
                is_risk = True
                reasons.append(f"late submissions {late_count} > 2")

            if is_risk:
                at_risk.append({
                    "student_id": s_id,
                    "name": s['name'],
                    "average_stress": avg_stress,
                    "late_submissions": late_count,
                    "reasons": reasons
                })
                
        conn.close()
        return at_risk
