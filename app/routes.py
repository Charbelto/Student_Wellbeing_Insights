from flask import Blueprint, render_template, current_app, jsonify, request
from app.database.models import StressLevel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    # For the prototype, we'll simulate data for a specific student or show system overview
    # Let's show data for student_id=1 by default
    student_id = 1
    
    # Ensure some data exists for demonstration if empty (optional, but good for first run)
    # In production, this wouldn't be here.
    if not current_app.attendance_service.get_student_attendance(student_id):
        # Seed some data
        from datetime import date
        current_app.attendance_service.record_attendance(student_id, "CS101", "Present", date.today())
    
    summary = current_app.analytics_service.get_student_wellbeing_summary(student_id)
    return render_template('dashboard.html', summary=summary)

@main_bp.route('/api/submit-survey', methods=['POST'])
def submit_survey():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    try:
        current_app.wellbeing_service.submit_survey(
            student_id=data['student_id'],
            stress_level=data['stress_level'],
            hours_slept=data['hours_slept'],
            comments=data.get('comments')
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

