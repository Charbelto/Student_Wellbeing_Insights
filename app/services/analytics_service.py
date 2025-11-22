from typing import List, Dict, Any
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService
from app.database.models import StressLevel

class AnalyticsService:
    def __init__(self, attendance_service: AttendanceService, wellbeing_service: WellbeingService, submission_service: SubmissionService):
        self.attendance_service = attendance_service
        self.wellbeing_service = wellbeing_service
        self.submission_service = submission_service

    def get_student_wellbeing_summary(self, student_id: int) -> Dict[str, Any]:
        attendance_avg = self.attendance_service.calculate_average_attendance(student_id)
        
        # Get wellbeing history
        history = self.wellbeing_service.get_student_history(student_id)
        avg_stress = 0
        avg_sleep = 0
        if history:
            avg_stress = sum(h.stress_level.value for h in history) / len(history)
            avg_sleep = sum(h.hours_slept for h in history) / len(history)
            
        return {
            "student_id": student_id,
            "average_attendance_pct": attendance_avg,
            "average_stress_level": avg_stress,
            "average_hours_slept": avg_sleep
        }

    def identify_high_stress_weeks(self, threshold: int = 4) -> List[Dict[str, Any]]:
        # This is a bit tricky with the current mock storage since we don't have a "get all surveys" method exposed in WellbeingService.
        # For now, I'll iterate through the private storage for demonstration, or I should add a method to WellbeingService.
        # To respect encapsulation/MVC, I should add a method to WellbeingService to get all surveys, or mock it here.
        # Since I can't easily change the interface of WellbeingService in the middle of this specific file write without multiple steps,
        # and `_storage` is accessible (protected convention), I will access it directly for this prototype phase or assume I can get all.
        # Better approach: The service should probably have `get_all_surveys()`.
        
        # However, looking at my WellbeingService implementation, it has `_storage`.
        # I will iterate `_storage` which is available on the instance.
        
        high_stress_reports = []
        for survey in self.wellbeing_service._storage:
            if survey.stress_level.value >= threshold:
                high_stress_reports.append({
                    "student_id": survey.student_id,
                    "date": survey.date,
                    "stress_level": survey.stress_level,
                    "comments": survey.comments
                })
        return high_stress_reports
