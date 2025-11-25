from flask import Blueprint, render_template, current_app, jsonify, request, redirect, url_for, flash
from datetime import date, datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/students')
def students():
    all_students = current_app.student_service.get_all_students()
    return render_template('students.html', students=all_students)

@main_bp.route('/students/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    email = request.form.get('email')
    
    try:
        current_app.student_service.create_student(name, email)
    except ValueError as e:
        return render_template('students.html', 
                             students=current_app.student_service.get_all_students(),
                             error=str(e))
        
    return redirect(url_for('main.students'))

# --- ATTENDANCE ROUTES ---

@main_bp.route('/attendance/<int:student_id>')
def attendance_list(student_id):
    student = current_app.student_service.get_student(student_id)
    if not student:
        return "Student not found", 404
        
    records = current_app.attendance_service.get_student_attendance(student_id)
    return render_template('attendance.html', student=student, records=records)

@main_bp.route('/attendance/add', methods=['POST'])
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
def update_attendance(record_id):
    student_id = request.args.get('student_id', type=int)
    status = request.form.get('status')
    current_app.attendance_service.update_attendance(record_id, status)
    return redirect(url_for('main.attendance_list', student_id=student_id))

@main_bp.route('/attendance/delete/<int:record_id>', methods=['POST'])
def delete_attendance(record_id):
    student_id = request.args.get('student_id', type=int)
    current_app.attendance_service.delete_attendance(record_id)
    return redirect(url_for('main.attendance_list', student_id=student_id))

# --- SUBMISSION ROUTES ---

@main_bp.route('/submissions/<int:student_id>')
def submission_list(student_id):
    student = current_app.student_service.get_student(student_id)
    if not student:
        return "Student not found", 404
    
    submissions = current_app.submission_service.get_student_submissions(student_id)
    return render_template('submissions.html', student=student, submissions=submissions)

@main_bp.route('/submissions/add', methods=['POST'])
def add_submission():
    student_id = request.form.get('student_id', type=int)
    assignment_id = request.form.get('assignment_id')
    date_str = request.form.get('submission_date')
    
    if date_str:
        d = datetime.fromisoformat(date_str)
    else:
        d = datetime.now()
    
    current_app.submission_service.submit_assignment(student_id, assignment_id, d)
    return redirect(url_for('main.submission_list', student_id=student_id))

@main_bp.route('/submissions/grade/<int:submission_id>', methods=['POST'])
def grade_submission(submission_id):
    student_id = request.args.get('student_id', type=int)
    grade = request.form.get('grade', type=float)
    
    current_app.submission_service.grade_submission(submission_id, grade)
    return redirect(url_for('main.submission_list', student_id=student_id))

@main_bp.route('/submissions/delete/<int:submission_id>', methods=['POST'])
def delete_submission(submission_id):
    student_id = request.args.get('student_id', type=int)
    current_app.submission_service.delete_submission(submission_id)
    return redirect(url_for('main.submission_list', student_id=student_id))

# --- DASHBOARD ROUTES ---

@main_bp.route('/dashboard')
def dashboard():
    student_id = request.args.get('student_id', type=int)
    
    if not student_id:
        students = current_app.student_service.get_all_students()
        if students:
            return redirect(url_for('main.dashboard', student_id=students[0].id))
        else:
            return render_template('dashboard.html', summary=None, error="No students found. Please add a student first.")
            
    summary = current_app.analytics_service.get_student_wellbeing_summary(student_id)
    student = current_app.student_service.get_student(student_id)
    all_students = current_app.student_service.get_all_students()
    
    return render_template('dashboard.html', summary=summary, student=student, all_students=all_students)

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
