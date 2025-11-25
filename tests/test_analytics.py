import pytest
from app.database.models import StressLevel

def test_get_student_wellbeing_summary(analytics_service, attendance_service, wellbeing_service, student_service):
    # Setup data
    s = student_service.create_student("S1", "s1@test.com")
    attendance_service.record_attendance(s.id, "CS101", "Present", "2023-10-01")
    wellbeing_service.submit_survey(s.id, 3, 7)
    
    summary = analytics_service.get_student_wellbeing_summary(s.id)
    
    assert summary["student_id"] == s.id
    assert summary["average_attendance_pct"] == 100.0
    assert summary["average_stress_level"] == 3.0
    assert summary["average_hours_slept"] == 7.0

def test_identify_high_stress_weeks(analytics_service, wellbeing_service, student_service):
    # Setup data for multiple students
    s1 = student_service.create_student("S1", "s1@test.com")
    s2 = student_service.create_student("S2", "s2@test.com")
    
    wellbeing_service.submit_survey(s1.id, 5, 4) # High stress
    wellbeing_service.submit_survey(s2.id, 2, 8) # Low stress
    
    high_stress_reports = analytics_service.identify_high_stress_weeks()
    
    assert len(high_stress_reports) == 1
    assert high_stress_reports[0]["student_id"] == s1.id
    assert high_stress_reports[0]["stress_level"] == StressLevel.VERY_HIGH
