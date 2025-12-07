from flask import Blueprint, render_template, current_app, jsonify, request, redirect, url_for, flash, abort, make_response, send_file
from flask_login import login_required, current_user
from datetime import date, datetime
from app.database.models import Role
import csv
import io
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

    # Extract required fields
    name = request.form.get('name')
    student_id = request.form.get('student_id')
    degree_id = request.form.get('degree_id')
    degree_name = request.form.get('degree_name')
    year = request.form.get('year')
    age_band = request.form.get('age_band')
    domicile = request.form.get('domicile')

    # Optional fields
    go_home_frequency = request.form.get('go_home_frequency')
    extracurricular_per_week = request.form.get('extracurricular_per_week')
    avg_commute_time_min = request.form.get('avg_commute_time_min')
    avg_screen_time_hours = request.form.get('avg_screen_time_hours')
    commute_type = request.form.get('commute_type')
    medical_information = request.form.get('medical_information')
    disabilities = request.form.get('disabilities')
    
    # Convert appropriate numeric fields
    try:
        degree_id = int(degree_id) if degree_id else None
        year = int(year) if year else None
        extracurricular_per_week = int(extracurricular_per_week) if extracurricular_per_week else None
        avg_commute_time_min = int(avg_commute_time_min) if avg_commute_time_min else None
        avg_screen_time_hours = int(avg_screen_time_hours) if avg_screen_time_hours else None
    except ValueError:
        flash("One or more numeric fields contain invalid values.", "error")
        return redirect(url_for('main.students'))

    try:
        current_app.student_service.create_student(
            name=name,
            student_id=student_id,
            degree_id=degree_id,
            degree_name=degree_name,
            year=year,
            age_band=age_band,
            domicile=domicile,
            go_home_frequency=go_home_frequency,
            extracurricular_per_week=extracurricular_per_week,
            avg_commute_time_min=avg_commute_time_min,
            avg_screen_time_hours=avg_screen_time_hours,
            commute_type=commute_type,
            medical_information=medical_information,
            disabilities=disabilities
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.students'))
        
    return redirect(url_for('main.students'))

# --- ATTENDANCE ROUTES ---

@main_bp.route('/attendance/<student_id>')
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
    student_id = request.form.get('student_id')
    module_id = request.form.get('module_id')
    action = request.form.get('action')

    if not student_id or not module_id or not action:
        flash("Missing attendance information.", "error")
        return redirect(url_for('main.students'))

    # Route to correct attendance update function
    if action == "present":
        current_app.attendance_service.record_attendance(student_id, module_id)
    elif action == "absent":
        current_app.attendance_service.record_absence(student_id, module_id)
    else:
        flash("Invalid attendance action.", "error")
        return redirect(url_for('main.attendance_list', student_id=student_id))

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

@main_bp.route('/submissions/<student_id>')
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
    student_id = request.form.get('student_id')
    module_id = request.form.get('module_id', type=int)
    semester = request.form.get('semester', type=int)
    deadline_dt = request.form.get('deadline_datetime')
    submitted_dt = request.form.get('submitted_datetime')
    early_late = request.form.get('early_late_submissions', type=int)
    mark = request.form.get('mark', type=float)
    late = request.form.get('late') in ['true', 'True', True]

    if not student_id or not module_id or not semester or not deadline_dt or not submitted_dt:
        flash("Missing submission information.", "error")
        return redirect(url_for('main.submission_list', student_id=student_id))

    try:
        current_app.submission_service.submit_assignment(
            submission_id=None,
            student_id=student_id,
            module_id=module_id,
            semester=semester,
            deadline_datetime=datetime.fromisoformat(deadline_dt),
            submitted_datetime=datetime.fromisoformat(submitted_dt),
            early_late_submissions=early_late or 0,
            mark=mark,
            late=late
        )
    except Exception as e:
        flash(f"Error adding submission: {e}", "error")

    return redirect(url_for('main.submission_list', student_id=student_id))

@main_bp.route('/submissions/grade/<int:submission_id>', methods=['POST'])
@login_required
def grade_submission(submission_id):
    student_id = request.args.get('student_id')
    grade = request.form.get('grade', type=float)
    
    current_app.submission_service.grade_submission(submission_id, grade)
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
    student_id = request.args.get('student_id')
    
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
        student.medical_information = "REDACTED"
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
        current_app.wellbeing_service.submit_survey(
            student_id=data['student_id'],
            week=data.get('week', 1),
            stress_level=data['stress_level'],
            hours_slept=data['hours_slept'],
            mood_score=data.get('mood_score', 0)
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

@main_bp.route('/api/dashboard/summary')
@login_required
def api_dashboard_summary():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({"error": "student_id required"}), 400
    summary = current_app.analytics_service.get_student_wellbeing_summary(student_id)
    if current_user.role != Role.WELLBEING_OFFICER:
        summary["average_stress_level"] = None
        summary["average_hours_slept"] = None
    return jsonify(summary)

@main_bp.route('/api/chart/stress_trend')
@login_required
def stress_trend():
    data = current_app.analytics_service.get_stress_trend()
    return jsonify(data)

@main_bp.route('/api/chart/attendance_vs_mark')
@login_required
def attendance_vs_mark():
    data = current_app.analytics_service.get_attendance_vs_mark()
    return jsonify(data)


@main_bp.route('/visualizations/stress_trend.png')
@login_required
def stress_trend_png():
    data = current_app.analytics_service.get_stress_trend()
    fig, ax = plt.subplots()
    ax.plot(data.get("weeks", []), data.get("avg_stress", []), marker='o', color='red')
    ax.set_xlabel("Week")
    ax.set_ylabel("Average Stress")
    ax.set_title("Average Stress Levels Over Time")
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle="--", alpha=0.4)
    img = io.BytesIO()
    fig.tight_layout()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@main_bp.route('/visualizations/attendance_vs_mark.png')
@login_required
def attendance_vs_mark_png():
    data = current_app.analytics_service.get_attendance_vs_mark()
    fig, ax = plt.subplots()
    if data:
        x_vals = [row["avg_attendance"] for row in data]
        y_vals = [row["avg_mark"] for row in data]
        ax.scatter(x_vals, y_vals, c='blue', alpha=0.7)
    ax.set_xlabel("Average Attendance")
    ax.set_ylabel("Average Mark")
    ax.set_title("Attendance vs Average Mark")
    ax.grid(True, linestyle="--", alpha=0.4)
    img = io.BytesIO()
    fig.tight_layout()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@main_bp.route('/api/feedback/summary')
@login_required
def feedback_summary():
    data = current_app.analytics_service.get_feedback_summary()
    return jsonify(data)

@main_bp.route('/api/import/submissions', methods=['POST'])
@login_required
def import_submissions():
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)
    raw = request.data.decode() if request.data else request.form.get('csv', '')
    if not raw:
        return jsonify({"status": "error", "message": "No CSV provided"}), 400
    reader = csv.DictReader(io.StringIO(raw))
    row_num = 1
    for row in reader:
        row_num += 1
        try:
            float(row.get("mark", ""))
        except ValueError:
            return jsonify({"status": "error", "message": f"Error in Row {row_num}: Mark must be a number"}), 400
    return jsonify({"status": "success", "rows_processed": row_num - 1})

@main_bp.route('/export/risk')
@login_required
def export_risk():
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)

    risks = current_app.analytics_service.identify_at_risk_students()
    si = io.StringIO()
    cw = csv.DictWriter(si, fieldnames=["student_id", "risk_reason"])
    cw.writeheader()
    for r in risks:
        cw.writerow({
            "student_id": r["student_id"],
            "risk_reason": "; ".join(r.get("reasons", []))
        })
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=risk_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main_bp.route('/api/students')
@login_required
def api_students():
    from app.database.connection import get_db_connection
    conn = get_db_connection(current_app.student_service.db_name)
    cur = conn.cursor()
    cur.execute("""
        SELECT student_names.name, students.student_id, students.degree_name, students.year,
               students.medical_information, students.disabilities
        FROM students
        LEFT JOIN student_names ON students.student_id = student_names.student_id
    """)
    rows = cur.fetchall()
    conn.close()
    role_val = getattr(current_user.role, "value", current_user.role)
    is_officer = str(role_val).lower() == "wellbeing_officer"
    payload = []
    for r in rows:
        med_info = r["medical_information"]
        dis = r["disabilities"]
        payload.append({
            "student_id": r["student_id"],
            "name": r["name"],
            "degree_name": r["degree_name"],
            "year": r["year"],
            "medical_information": (med_info or "N/A") if is_officer else None,
            "disabilities": (dis or "N/A") if is_officer else None,
        })
    return jsonify(payload)

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
