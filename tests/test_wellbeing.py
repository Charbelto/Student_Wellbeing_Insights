import pytest
from datetime import date
from app.database.models import WellbeingSurvey, StressLevel

def test_submit_survey(wellbeing_service):
    student_id = 1
    stress_level = 3
    hours_slept = 7.5
    comments = "Feeling okay"
    
    survey = wellbeing_service.submit_survey(student_id, stress_level, hours_slept, comments)
    
    assert isinstance(survey, WellbeingSurvey)
    assert survey.stress_level == StressLevel.MODERATE
    assert survey.hours_slept == 7.5
    assert survey.comments == comments

def test_submit_survey_validation_error(wellbeing_service):
    with pytest.raises(ValueError):
        wellbeing_service.submit_survey(1, 6, 8)

def test_get_student_history(wellbeing_service):
    wellbeing_service.submit_survey(1, 2, 8)
    wellbeing_service.submit_survey(1, 4, 6)
    
    history = wellbeing_service.get_student_history(1)
    assert len(history) == 2
    assert history[0].stress_level == StressLevel.LOW
    assert history[1].stress_level == StressLevel.HIGH

