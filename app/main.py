from datetime import date, datetime
from app.services.attendance_service import AttendanceService
from app.services.wellbeing_service import WellbeingService
from app.services.submission_service import SubmissionService
from app.services.analytics_service import AnalyticsService
from app.database.models import StressLevel

def main():
    print("=== Student Wellbeing System Prototype ===")

    # Initialize services
    attendance_service = AttendanceService()
    wellbeing_service = WellbeingService()
    submission_service = SubmissionService()
    analytics_service = AnalyticsService(attendance_service, wellbeing_service, submission_service)

    # Simulate some data
    print("\n--> Recording Attendance...")
    attendance_service.record_attendance(1, "CS101", "Present", date(2023, 10, 1))
    attendance_service.record_attendance(1, "CS101", "Absent", date(2023, 10, 8))
    attendance_service.record_attendance(1, "CS101", "Present", date(2023, 10, 15))
    print("Recorded 3 attendance records for Student 1.")

    print("\n--> Submitting Wellbeing Surveys...")
    wellbeing_service.submit_survey(1, 2, 8, "Feeling good")
    wellbeing_service.submit_survey(1, 4, 5, "Stressed about deadlines")
    print("Recorded 2 surveys for Student 1.")

    print("\n--> Submitting Assignments...")
    s1 = submission_service.submit_assignment(1, "A1", datetime.now())
    submission_service.grade_submission(s1.id, 85.5)
    print(f"Recorded assignment A1 for Student 1 with grade 85.5")

    # Analytics
    print("\n--> Running Analytics...")
    summary = analytics_service.get_student_wellbeing_summary(1)
    print(f"Student 1 Summary: {summary}")

    high_stress = analytics_service.identify_high_stress_weeks(threshold=4)
    print(f"High Stress Reports: {len(high_stress)} found.")
    for report in high_stress:
        print(f" - Date: {report['date']}, Stress: {report['stress_level'].name}, Comment: {report['comments']}")

    # CRUD Demo
    print("\n--> Demonstrating Delete Operation...")
    print(f"Attendance records before delete: {len(attendance_service.get_student_attendance(1))}")
    last_attendance = attendance_service.get_student_attendance(1)[-1]
    attendance_service.delete_attendance(last_attendance.id)
    print(f"Attendance records after delete: {len(attendance_service.get_student_attendance(1))}")

if __name__ == "__main__":
    main()

