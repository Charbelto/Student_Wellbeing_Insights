from flask import Blueprint, render_template, current_app, jsonify, request, redirect, url_for, flash, abort, make_response
from flask_login import login_required, current_user
from datetime import date, datetime
from app.database.models import Role
import csv
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    if current_user.role == Role.WELLBEING_OFFICER:
        return redirect(url_for('main.officer_dashboard'))
    elif current_user.role == Role.MODULE_LEADER:
        return redirect(url_for('main.students'))
    return render_template('index.html')

@main_bp.route('/officer_dashboard')
@login_required
def officer_dashboard():
    if current_user.role != Role.WELLBEING_OFFICER:
        flash("Access denied. Wellbeing Officer only.", "error")
        return redirect(url_for('main.index'))
        
    at_risk_students = current_app.analytics_service.identify_at_risk_students()
    return render_template('officer_dashboard.html', at_risk_students=at_risk_students)

@main_bp.route('/students')
@login_required
def students():
    all_students = current_app.student_service.get_all_students()
    return render_template('students.html', students=all_students)

@main_bp.route('/students/add', methods=['POST'])
@login_required
def add_student():
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)

    name = request.form.get('name')
    email = request.form.get('email')
    
    try:
        current_app.student_service.create_student(university_id=name, name=name, email=email)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.students'))
        
    return redirect(url_for('main.students'))

# --- ATTENDANCE ROUTES ---

@main_bp.route('/attendance/<int:student_id>')
@login_required
def attendance_list(student_id):
    student = current_app.student_service.get_student(student_id)
    if not student:
        abort(404)
        
    records = current_app.attendance_service.get_student_attendance(student_id)
    return render_template('attendance.html', student=student, records=records)

@main_bp.route('/attendance/add', methods=['POST'])
@login_required
def add_attendance():
    student_id = request.form.get('student_id', type=int)
    course_id = request.form.get('course_id')
    status = request.form.get('status')
    date_str = request.form.get('date')
    
    if date_str:
        d = date.fromisoformat(date_str)
    else:
        d = date.today()
        
    current_app.attendance_service.record_attendance(student_id, course_id, status, d)
    return redirect(url_for('main.attendance_list', student_id=student_id))

@main_bp.route('/attendance/update/<int:record_id>', methods=['POST'])
@login_required
def update_attendance(record_id):
    student_id = request.args.get('student_id', type=int)
    status = request.form.get('status')
    current_app.attendance_service.update_attendance(record_id, status)
    return redirect(url_for('main.attendance_list', student_id=student_id))

@main_bp.route('/attendance/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_attendance(record_id):
    student_id = request.args.get('student_id', type=int)
    current_app.attendance_service.delete_attendance(record_id)
    return redirect(url_for('main.attendance_list', student_id=student_id))

# --- SUBMISSION ROUTES ---

@main_bp.route('/submissions/<int:student_id>')
@login_required
def submission_list(student_id):
    student = current_app.student_service.get_student(student_id)
    if not student:
        abort(404)
    
    submissions = current_app.submission_service.get_student_submissions(student_id)
    return render_template('submissions.html', student=student, submissions=submissions)

@main_bp.route('/submissions/add', methods=['POST'])
@login_required
def add_submission():
    student_id = request.form.get('student_id') # Keep as string/text per schema
    module_id = request.form.get('module_id', type=int)
    date_str = request.form.get('submission_date')
    deadline_str = request.form.get('deadline')
    
    if not module_id:
        flash("Module ID is required", "error")
        return redirect(url_for('main.submission_list', student_id=student_id))

    if date_str:
        submitted_d = datetime.fromisoformat(date_str)
    else:
        submitted_d = datetime.now()
        
    if deadline_str:
        deadline_d = datetime.fromisoformat(deadline_str)
    else:
        # Default to submitted date (not late)
        deadline_d = submitted_d
    
    try:
        current_app.submission_service.submit_assignment(
            student_id=student_id, 
            module_id=module_id, 
            semester=1, # Default
            deadline_datetime=deadline_d,
            submitted_datetime=submitted_d
        )
    except Exception as e:
        flash(f"Error adding submission: {e}", "error")

    return redirect(url_for('main.submission_list', student_id=student_id))

@main_bp.route('/submissions/grade/<int:submission_id>', methods=['POST'])
@login_required
def grade_submission(submission_id):
    student_id = request.args.get('student_id')
    mark = request.form.get('mark', type=float)
    
    current_app.submission_service.grade_submission(submission_id, mark)
    return redirect(url_for('main.submission_list', student_id=student_id))

@main_bp.route('/submissions/delete/<int:submission_id>', methods=['POST'])
@login_required
def delete_submission(submission_id):
    student_id = request.args.get('student_id')
    current_app.submission_service.delete_submission(submission_id)
    return redirect(url_for('main.submission_list', student_id=student_id))

# --- DASHBOARD ROUTES ---

@main_bp.route('/dashboard')
@login_required
def dashboard():
    student_id = request.args.get('student_id', type=int)
    
    if not student_id:
        students = current_app.student_service.get_all_students()
        if students:
            return redirect(url_for('main.dashboard', student_id=students[0].id))
        else:
            return render_template('dashboard.html', summary=None, error="No students found.")
    
    student = current_app.student_service.get_student(student_id)
    all_students = current_app.student_service.get_all_students()
    summary = current_app.analytics_service.get_student_wellbeing_summary(student_id)
    
    if current_user.role != Role.WELLBEING_OFFICER:
        summary['average_stress_level'] = None
        summary['average_hours_slept'] = None
        history = None
        student.medical_info = "REDACTED"
        student.disabilities = "REDACTED"
    else:
        history = current_app.analytics_service.get_student_wellbeing_history(student_id)
    
    return render_template('dashboard.html', summary=summary, history=history, student=student, all_students=all_students)

@main_bp.route('/api/submit-survey', methods=['POST'])
@login_required
def submit_survey():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    try:
        # week defaults to 1 if not provided
        current_app.wellbeing_service.submit_survey(
            student_id=data['student_id'],
            stress_level=data['stress_level'],
            hours_slept=data['hours_slept'],
            mood_score=data.get('mood_score', 5),
            week=data.get('week', 1)
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@main_bp.route('/export/students')
@login_required
def export_students():
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)
        
    students = current_app.student_service.get_all_students()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'University ID', 'Name', 'Email', 'Degree', 'Year', 'Medical Info', 'Disabilities'])
    
    for s in students:
        cw.writerow([s.id, getattr(s, 'university_id', ''), s.name, s.email, s.degree_name, getattr(s, 'year', ''), s.medical_info, s.disabilities])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=students_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)
    
    try:
        current_app.student_service.delete_student(student_id)
        flash('Student data deleted successfully.', 'success')
    except Exception as e:
        flash(str(e), 'error')
        
    return redirect(url_for('main.students'))
