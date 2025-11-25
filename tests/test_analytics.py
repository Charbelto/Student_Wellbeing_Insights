import pytest
from app.database.models import StressLevel

def test_get_student_wellbeing_summary(analytics_service, attendance_service, wellbeing_service, student_service):
    # Setup data
    s = student_service.create_student("u1", "S1", "s1@test.com")
    attendance_service.record_attendance(s.id, "CS101", "Present", "2023-10-01")
    wellbeing_service.submit_survey(s.id, 3, 7)
    
    summary = analytics_service.get_student_wellbeing_summary(s.id)
    
    assert summary["student_id"] == s.id
    assert summary["average_attendance_pct"] == 100.0
    assert summary["average_stress_level"] == 3.0
    assert summary["average_hours_slept"] == 7.0

def test_identify_at_risk_students(analytics_service, wellbeing_service, student_service):
    # Setup data for multiple students
    s1 = student_service.create_student("u1", "S1", "s1@test.com")
    s2 = student_service.create_student("u2", "S2", "s2@test.com")
    
    # S1: High stress
    wellbeing_service.submit_survey(s1.id, 5, 4)
    wellbeing_service.submit_survey(s1.id, 5, 4)
    
    # S2: Low stress
    wellbeing_service.submit_survey(s2.id, 2, 8)
    
    risks = analytics_service.identify_at_risk_students()
    
    assert len(risks) == 1
    assert risks[0]["student_id"] == s1.id
    assert "High Average Stress" in risks[0]["reasons"][0]
