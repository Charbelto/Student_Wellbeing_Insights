from flask import Flask
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService
from app.services.analytics_service import AnalyticsService
from app.services.student_service import StudentService

def create_app():
    app = Flask(__name__)
    
    # Initialize Services
    # In a real app, these might be singletons or injected dependencies
    # We attach them to the app instance for easy access in routes
    app.student_service = StudentService()
    app.attendance_service = AttendanceService()
    app.wellbeing_service = WellbeingService()
    app.submission_service = SubmissionService()
    app.analytics_service = AnalyticsService(
        app.attendance_service, 
        app.wellbeing_service, 
        app.submission_service
    )
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
