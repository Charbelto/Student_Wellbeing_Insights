import pytest
from app.services.attendance_service import AttendanceService
from app.services.submission_service import SubmissionService
from app.services.wellbeing_service import WellbeingService
from app.services.analytics_service import AnalyticsService
from app import create_app

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

@pytest.fixture
def app():
    # Create an app instance for testing
    # We can inject mock services here if we change create_app to accept them,
    # or we can rely on the app creating its own services for integration tests.
    # For simplicity in this prototype, we'll let the app create its own, 
    # but typically we'd want to mock them or use the fixtures above.
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()
