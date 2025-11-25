import pytest
import os
import sqlite3
from app.services.attendance_service import AttendanceService
from app.services.submission_service import SubmissionService
from app.services.wellbeing_service import WellbeingService
from app.services.analytics_service import AnalyticsService
from app import create_app

TEST_DB = 'test_wellbeing_conftest.db'

@pytest.fixture(scope='function')
def db_setup():
    """Creates a new database for each test function."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        
    # Initialize DB
    conn = sqlite3.connect(TEST_DB)
    with open('app/database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    yield TEST_DB
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.fixture
def attendance_service(db_setup):
    return AttendanceService(db_name=db_setup)

@pytest.fixture
def submission_service(db_setup):
    return SubmissionService(db_name=db_setup)

@pytest.fixture
def wellbeing_service(db_setup):
    return WellbeingService(db_name=db_setup)

@pytest.fixture
def analytics_service(attendance_service, wellbeing_service, submission_service):
    return AnalyticsService(attendance_service, wellbeing_service, submission_service)

@pytest.fixture
def app(attendance_service, wellbeing_service, submission_service, analytics_service):
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    # Inject test services using the test DB
    app.attendance_service = attendance_service
    app.wellbeing_service = wellbeing_service
    app.submission_service = submission_service
    app.analytics_service = analytics_service
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()
