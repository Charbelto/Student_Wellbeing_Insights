import pytest
from app.services.attendance_service import AttendanceService
from app.services.submission_service import SubmissionService
from app.services.wellbeing_service import WellbeingService
from app.services.analytics_service import AnalyticsService

@pytest.fixture
def attendance_service():
    return AttendanceService()

@pytest.fixture
def submission_service():
    return SubmissionService()

@pytest.fixture
def wellbeing_service():
    return WellbeingService()

@pytest.fixture
def analytics_service(attendance_service, wellbeing_service, submission_service):
    return AnalyticsService(attendance_service, wellbeing_service, submission_service)

