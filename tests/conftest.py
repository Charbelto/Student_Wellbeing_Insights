import pytest
import os
import sqlite3
import uuid
import time
from app.services.attendance_service import AttendanceService
from app.services.submission_service import SubmissionService
from app.services.wellbeing_service import WellbeingService
from app.services.analytics_service import AnalyticsService
from app.services.student_service import StudentService
from app.services.user_service import UserService
from app.database.models import Role
from app import create_app

@pytest.fixture(scope='function')
def db_setup():
    """Creates a new database for each test function."""
    # Use a unique filename for each test to avoid Windows file lock issues (WinError 32)
    # This prevents trying to delete a file that might still be closing from a previous test
    db_name = f"test_wellbeing_{uuid.uuid4().hex}.db"
    
    # Initialize DB
    conn = sqlite3.connect(db_name)
    with open('app/database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    yield db_name
    
    # Cleanup with retry logic for robustness
    for _ in range(10):
        try:
            if os.path.exists(db_name):
                os.remove(db_name)
            break
        except PermissionError:
            # Wait a bit for the file lock to release
            time.sleep(0.1)

@pytest.fixture
def student_service(db_setup):
    return StudentService(db_name=db_setup)

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
def user_service(db_setup):
    return UserService(db_name=db_setup)

@pytest.fixture
def analytics_service(attendance_service, wellbeing_service, submission_service, db_setup):
    return AnalyticsService(attendance_service, wellbeing_service, submission_service, db_name=db_setup)

@pytest.fixture
def app(student_service, attendance_service, wellbeing_service, submission_service, analytics_service, user_service):
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "dev",
        "WTF_CSRF_ENABLED": False # Disable CSRF for tests
    })
    # Inject test services using the test DB
    app.student_service = student_service
    app.attendance_service = attendance_service
    app.wellbeing_service = wellbeing_service
    app.submission_service = submission_service
    app.analytics_service = analytics_service
    app.user_service = user_service
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, user_service):
    # Create a user and login
    user_service.create_user("test_admin", "pass", Role.WELLBEING_OFFICER)
    with client.session_transaction() as sess:
        # Flask-Login session management simulation or just use post login
        pass
    client.post('/login', data={'username': 'test_admin', 'password': 'pass'}, follow_redirects=True)
    return client
