from app import create_app
from app.database.connection import init_db, get_db_connection
from app.database.models import Role
from app.services.student_service import StudentService
import os
import logging


def seed_default_users(app):
    """Create baseline users if they do not exist."""
    usvc = app.user_service
    for username, password, role in [
        ("officer", "officer123", Role.WELLBEING_OFFICER),
        ("tutor", "tutor123", Role.TUTOR),
        ("leader", "lead123", Role.MODULE_LEADER),
    ]:
        existing = usvc.get_user_by_username(username)
        if not existing:
            usvc.create_user(username, password, role)
            print(f"Seeded user: {username}/{password} ({role.value})")
        else:
            # Refresh password to ensure known credentials keep working
            usvc.reset_password(username, password)


def ensure_schema():
    """
    Create any core tables that might be missing without dropping data.
    This is a safe guard for dev environments where the DB was created
    before schema updates.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS student_names (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        );
        """
    )
    conn.commit()
    conn.close()


def seed_demo_students():
    """
    Seed a small demo student if none exist so the UI has data to show.
    This runs only when the students table is empty.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM students")
    row = cur.fetchone()
    if row and row["c"] == 0:
        # Ensure a degree exists for FK
        cur.execute(
            "INSERT OR IGNORE INTO degrees(degree_id, degree_name) VALUES(1, 'Computing')"
        )
        # Insert demo student
        cur.execute(
            """
            INSERT INTO students(
                student_id, degree_id, degree_name, year, age_band, domicile,
                go_home_frequency, extracurricular_per_week, avg_commute_time_min,
                avg_screen_time_hours, commute_type, medical_information, disabilities
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "S1001",
                1,
                "Computing",
                1,
                "18-21",
                "UK",
                "Weekly",
                2,
                30,
                5,
                "Bus",
                "None",
                "None",
            ),
        )
        cur.execute(
            "INSERT OR IGNORE INTO student_names(student_id, name) VALUES(?, ?)",
            ("S1001", "Demo Student"),
        )
        conn.commit()
        print("Seeded demo student: S1001 / Demo Student")
    conn.close()


def import_students_from_excel_if_empty(app, path="app/database/PAI_finalised.xlsx"):
    """
    Import data from Excel only if the students table is empty (or has <=1 rows).
    Sheets expected (case-insensitive):
      - students
      - student names
      - degrees
      - modules
      - submissions
      - module feedback
      - risk indicators
      - survey
      - attendance
    Missing sheets are skipped gracefully.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM students")
    row = cur.fetchone()
    existing = row["c"] if row else 0
    # Allow import if the table is empty or only contains the single demo row
    if existing > 1:
        conn.close()
        print(f"Seed skipped: students table already has {existing} rows.")
        return
    conn.close()

    if not os.path.exists(path):
        logging.warning(f"Seed skipped: {path} not found.")
        return

    try:
        import pandas as pd  # type: ignore
    except ImportError:
        logging.warning("Seed skipped: pandas not installed. Install pandas/openpyxl to import Excel.")
        return

    try:
        xls = pd.ExcelFile(path)
    except Exception as exc:
        logging.warning(f"Seed skipped: failed to read {path}: {exc}")
        return

    svc = app.student_service if hasattr(app, "student_service") else StudentService()

    def parse_sheet(name):
        for candidate in xls.sheet_names:
            if candidate.strip().lower() == name:
                return xls.parse(candidate)
        return None

    def to_int(val, default=None):
        try:
            return int(val)
        except Exception:
            return default

    def to_float(val, default=None):
        try:
            return float(val)
        except Exception:
            return default

    def to_str(val, default=None):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return str(val)

    # Load sheets
    df_students = parse_sheet("students")
    df_names = parse_sheet("student names")
    df_degrees = parse_sheet("degrees")
    df_modules = parse_sheet("modules")
    df_submissions = parse_sheet("submissions")
    df_feedback = parse_sheet("module feedback")
    df_risk = parse_sheet("risk indicators")
    df_survey = parse_sheet("survey")
    df_attendance = parse_sheet("attendance")

    # Map student_id -> name
    name_map = {}
    if df_names is not None:
        for _, row in df_names.iterrows():
            sid = to_str(row.get("student_id"))
            nm = to_str(row.get("name"))
            if sid and nm:
                name_map[sid] = nm

    conn = get_db_connection()
    cur = conn.cursor()

    # Degrees
    if df_degrees is not None:
        for _, row in df_degrees.iterrows():
            did = to_int(row.get("degree_id"))
            dname = to_str(row.get("degree_name"), "General Studies")
            if did:
                cur.execute(
                    "INSERT OR IGNORE INTO degrees(degree_id, degree_name) VALUES(?, ?)",
                    (did, dname),
                )
    conn.commit()

    # Modules
    if df_modules is not None:
        for _, row in df_modules.iterrows():
            mid = to_int(row.get("module_id"))
            did = to_int(row.get("degree_id"))
            code = to_str(row.get("code"))
            name = to_str(row.get("name"))
            semester = to_int(row.get("semester"))
            lecture_day = to_str(row.get("lecture_day"))
            lecture_time = to_str(row.get("lecture_time"))
            difficulty = to_str(row.get("difficulty_level"))
            if mid and did and code and name and semester and lecture_day and lecture_time:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO modules(
                        module_id, degree_id, code, name, semester, lecture_day, lecture_time, difficulty_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (mid, did, code, name, semester, lecture_day, lecture_time, difficulty),
                )
    conn.commit()

    # Students (+ names)
    imported = 0
    if df_students is not None:
        for _, row in df_students.iterrows():
            sid = to_str(row.get("student_id"))
            if not sid:
                continue
            degree_id = to_int(row.get("degree_id"), 1)
            degree_name = to_str(row.get("degree_name"), "General Studies")
            year = to_int(row.get("year"), 1)
            age_band = to_str(row.get("age_band"), "18-21")
            domicile = to_str(row.get("domicile"), "UK")
            go_home_frequency = to_str(row.get("go_home_frequency"))
            extracurricular_per_week = to_int(row.get("extracurricular_per_week"))
            avg_commute_time_min = to_int(row.get("avg_commute_time_min"))
            avg_screen_time_hours = to_int(row.get("avg_screen_time_hours"))
            commute_type = to_str(row.get("commute_type"))
            medical_information = to_str(row.get("medical_information"))
            disabilities = to_str(row.get("disabilities"))
            name = name_map.get(sid) or sid
            try:
                svc.create_student(
                    name=name,
                    student_id=sid,
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
                    disabilities=disabilities,
                )
                imported += 1
            except Exception as exc:
                logging.warning(f"Row import skipped for student_id={sid}: {exc}")

    conn = get_db_connection()
    cur = conn.cursor()

    # Attendance
    if df_attendance is not None:
        for _, row in df_attendance.iterrows():
            sid = to_str(row.get("student_id"))
            mid = to_int(row.get("module_id"))
            total = to_int(row.get("total_sessions"), 0)
            attended = to_int(row.get("attended_sessions"), 0)
            rate = to_float(row.get("attendance_rate"), 0.0)
            if sid and mid:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO attendance(
                        student_id, module_id, total_sessions, attended_sessions, attendance_rate
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (sid, mid, total, attended, rate),
                )
    conn.commit()

    # Submissions
    if df_submissions is not None:
        for _, row in df_submissions.iterrows():
            sid = to_str(row.get("student_id"))
            mid = to_int(row.get("module_id"))
            sub_id = to_int(row.get("submission_id"))
            semester = to_int(row.get("semester"), 1)
            deadline = to_str(row.get("deadline_datetime"))
            submitted = to_str(row.get("submitted_datetime"))
            early_late = to_int(row.get("early_late_submissions"), 0)
            mark = to_float(row.get("mark"))
            late = bool(row.get("late")) if row.get("late") not in (None, "", 0, False) else False
            if sid and mid and sub_id and deadline and submitted:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO submissions(
                        submission_id, student_id, module_id, semester, deadline_datetime,
                        submitted_datetime, early_late_submissions, mark, late
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (sub_id, sid, mid, semester, deadline, submitted, early_late, mark, late),
                )
    conn.commit()

    # Survey
    if df_survey is not None:
        for _, row in df_survey.iterrows():
            sid = to_str(row.get("student_id"))
            week = to_int(row.get("week"))
            stress = to_int(row.get("stress_level"))
            hours = to_int(row.get("hours_slept"))
            mood = to_int(row.get("mood_score"))
            if sid and week is not None and stress is not None and hours is not None and mood is not None:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO survey(
                        student_id, week, stress_level, hours_slept, mood_score
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (sid, week, stress, hours, mood),
                )
    conn.commit()

    # Module feedback
    if df_feedback is not None:
        for _, row in df_feedback.iterrows():
            fid = to_str(row.get("feedback_id"))
            sid = to_str(row.get("student_id"))
            mid = to_int(row.get("module_id"))
            ec = to_int(row.get("engaging_content"))
            cq = to_int(row.get("comfortable_asking_questions"))
            pace = to_int(row.get("pace_rating"))
            prep = to_int(row.get("prepared_for_exams"))
            hours = to_int(row.get("hours_outside_class"))
            if fid and sid and mid:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO module_feedback(
                        feedback_id, student_id, module_id, engaging_content,
                        comfortable_asking_questions, pace_rating, prepared_for_exams, hours_outside_class
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (fid, sid, mid, ec, cq, pace, prep, hours),
                )
    conn.commit()

    # Risk indicators
    if df_risk is not None:
        for _, row in df_risk.iterrows():
            sid = to_str(row.get("student_id"))
            avg_stress = to_float(row.get("avg_stress"), 0)
            late_subs = to_int(row.get("late_submissions"), 0)
            avg_mark = to_float(row.get("avg_mark"), 0)
            min_mark = to_float(row.get("min_mark"), 0)
            max_mark = to_float(row.get("max_mark"), 0)
            risk_level = to_str(row.get("risk_level"), "Medium")
            if sid:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO risk_indicator(
                        student_id, avg_stress, late_submissions, avg_mark, min_mark, max_mark, risk_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (sid, avg_stress, late_subs, avg_mark, min_mark, max_mark, risk_level),
                )
    conn.commit()
    conn.close()

    if imported > 0:
        print(f"Imported {imported} students from {path}")
    else:
        logging.warning("No students imported from Excel; falling back to demo seeding.")


app = create_app()

if __name__ == "__main__":
    # Initialize DB if it doesn't exist (simplistic check)
    if not os.path.exists('wellbeing.db'):
        print("Initializing database...")
        init_db()
    else:
        # Ensure schema is present when reusing an existing DB
        ensure_schema()

    # Import real students if available; otherwise a small demo record will be added
    import_students_from_excel_if_empty(app)
    # Ensure at least one student for UI demo
    seed_demo_students()
    # Ensure defaults exist even on existing or freshly created DB
    seed_default_users(app)
    app.run(debug=True)
