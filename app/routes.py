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
    history = current_app.analytics_service.get_student_wellbeing_history(student_id)
    student = current_app.student_service.get_student(student_id)
    all_students = current_app.student_service.get_all_students()
    
    return render_template('dashboard.html', summary=summary, history=history, student=student, all_students=all_students)
