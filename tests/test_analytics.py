import pytest
from app.database.models import StressLevel

def test_get_student_wellbeing_summary(analytics_service, attendance_service, wellbeing_service):
    # Setup data
    attendance_service.record_attendance(1, "CS101", "Present", "2023-10-01")
    wellbeing_service.submit_survey(1, 3, 7)
    
    summary = analytics_service.get_student_wellbeing_summary(1)
    
    assert summary["student_id"] == 1
    assert summary["average_attendance_pct"] == 100.0
    assert summary["average_stress_level"] == 3.0
    assert summary["average_hours_slept"] == 7.0

def test_identify_high_stress_weeks(analytics_service, wellbeing_service):
    # Setup data for multiple students
    wellbeing_service.submit_survey(1, 5, 4) # High stress
    wellbeing_service.submit_survey(2, 2, 8) # Low stress
    
    high_stress_reports = analytics_service.identify_high_stress_weeks()
    
    assert len(high_stress_reports) == 1
    assert high_stress_reports[0]["student_id"] == 1
    assert high_stress_reports[0]["stress_level"] == StressLevel.VERY_HIGH
