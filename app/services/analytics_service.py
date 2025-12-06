from typing import List, Dict, Any
from app.database.connection import get_db_connection
import app.database.queries as q


class AnalyticsService:
    def __init__(self, attendance_service, wellbeing_service, submission_service, db_name: str = 'wellbeing.db'):
        self.attendance_service = attendance_service
        self.wellbeing_service = wellbeing_service
        self.submission_service = submission_service
        self.db_name = db_name

    def get_student_wellbeing_summary(self, student_id: int) -> Dict[str, Any]:
        attendance_pct = self.attendance_service.calculate_average_attendance(student_id)

        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_WELLBEING_AVERAGES, (student_id,))
        row = cursor.fetchone()
        conn.close()

        avg_stress = row["avg_stress"] if row and row["avg_stress"] is not None else 0.0
        avg_sleep = row["avg_sleep"] if row and row["avg_sleep"] is not None else 0.0

        return {
            "student_id": student_id,
            "average_attendance_pct": attendance_pct,
            "average_attendance_rate": attendance_pct,
            "average_stress_level": avg_stress,
            "average_hours_slept": avg_sleep,
        }

    def get_student_wellbeing_history(self, student_id: int, limit: int = 30) -> Dict[str, List[Any]]:
        history = self.wellbeing_service.get_student_history(student_id)[:limit]
        return {
            "timestamps": [survey.created_at.isoformat() for survey in history],
            "stress_levels": [survey.stress_level.value for survey in history],
            "hours_slept": [survey.hours_slept for survey in history],
        }

    def identify_at_risk_students(self) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_ALL_STUDENTS)
        students = cursor.fetchall()
        conn.close()

        at_risk = []
        for row in students:
            student_id = row["id"]
            summary = self.get_student_wellbeing_summary(student_id)
            reasons = []
            attendance_records = self.attendance_service.get_student_attendance(student_id)
            if summary["average_stress_level"] >= 4.0:
                reasons.append(f"High Average Stress ({summary['average_stress_level']:.1f})")
            if attendance_records and summary["average_attendance_pct"] < 50.0:
                reasons.append(f"Low Attendance ({summary['average_attendance_pct']:.1f}%)")

            if reasons:
                at_risk.append(
                    {
                        "student_id": student_id,
                        "name": row["name"],
                        "reasons": reasons,
                    }
                )
        return at_risk
