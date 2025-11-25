from flask import Blueprint, render_template, current_app, jsonify, request, redirect, url_for, flash

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
        # flash('Student added successfully!', 'success') # Need secret key for flash
    except ValueError as e:
        # flash(str(e), 'error')
        return render_template('students.html', 
                             students=current_app.student_service.get_all_students(),
                             error=str(e))
        
    return redirect(url_for('main.students'))

@main_bp.route('/dashboard')
def dashboard():
    # If student_id is passed, show for that student, else show list or default
    student_id = request.args.get('student_id', type=int)
    
    if not student_id:
        # If no student selected, try to pick the first one or show empty state
        students = current_app.student_service.get_all_students()
        if students:
            return redirect(url_for('main.dashboard', student_id=students[0].id))
        else:
            # No students at all
            return render_template('dashboard.html', summary=None, error="No students found. Please add a student first.")
            
    summary = current_app.analytics_service.get_student_wellbeing_summary(student_id)
    # Also fetch student details to display name
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
