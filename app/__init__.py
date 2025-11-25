from flask import Flask
from flask_login import LoginManager
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService
from app.services.analytics_service import AnalyticsService
from app.services.student_service import StudentService
from app.services.user_service import UserService

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod' # Required for sessions
    
    # Initialize Services
    app.student_service = StudentService()
    app.attendance_service = AttendanceService()
    app.wellbeing_service = WellbeingService()
    app.submission_service = SubmissionService()
    app.user_service = UserService()
    app.analytics_service = AnalyticsService(
        app.attendance_service, 
        app.wellbeing_service, 
        app.submission_service
    )
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return app.user_service.get_user_by_id(int(user_id))
    
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app
