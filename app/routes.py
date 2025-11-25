import csv
import io
from flask import Response, make_response

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
        cw.writerow([s.id, s.university_id, s.name, s.email, s.degree_name, s.year, s.medical_info, s.disabilities])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=students_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != Role.WELLBEING_OFFICER:
        abort(403)
        
    # We need to implement delete_student in service to cascade deletes or handle it here
    # For prototype, we'll delete from DB directly or add method to service.
    # Adding method to service is better.
    
    try:
        current_app.student_service.delete_student(student_id)
        flash('Student data deleted successfully.', 'success')
    except Exception as e:
        flash(str(e), 'error')
        
    return redirect(url_for('main.students'))
