"""
Central place for all SQL used by the services.
Keeping the statements in one module avoids scattering raw SQL strings
throughout the codebase and makes the tests easier to reason about.
"""

# ---------------- USERS ----------------
INSERT_USER = """
    INSERT INTO users (username, password_hash, role)
    VALUES (?, ?, ?);
"""

GET_USER_BY_ID = """
    SELECT *
    FROM users
    WHERE id = ?;
"""

GET_USER_BY_USERNAME = """
    SELECT *
    FROM users
    WHERE username = ?;
"""

UPDATE_USER = """
    UPDATE users
    SET username = ?, password_hash = ?, role = ?
    WHERE id = ?;
"""

DELETE_USER = """
    DELETE FROM users
    WHERE id = ?;
"""

# ---------------- STUDENTS ----------------
INSERT_STUDENT = """
    INSERT INTO students (university_id, name, email, degree_name, year, medical_info, disabilities)
    VALUES (?, ?, ?, ?, ?, ?, ?);
"""

GET_STUDENT_BY_ID = """
    SELECT *
    FROM students
    WHERE id = ?;
"""

GET_STUDENT_BY_UNIVERSITY_ID = """
    SELECT *
    FROM students
    WHERE university_id = ?;
"""

GET_ALL_STUDENTS = """
    SELECT *
    FROM students
    ORDER BY name ASC;
"""

DELETE_STUDENT = """
    DELETE FROM students
    WHERE id = ?;
"""

# ---------------- ATTENDANCE ----------------
INSERT_ATTENDANCE = """
    INSERT INTO attendance (student_id, course_id, status, date)
    VALUES (?, ?, ?, ?);
"""

GET_ATTENDANCE_BY_ID = """
    SELECT *
    FROM attendance
    WHERE id = ?;
"""

GET_ATTENDANCE_FOR_STUDENT = """
    SELECT *
    FROM attendance
    WHERE student_id = ?
    ORDER BY date ASC;
"""

UPDATE_ATTENDANCE_STATUS = """
    UPDATE attendance
    SET status = ?
    WHERE id = ?;
"""

DELETE_ATTENDANCE = """
    DELETE FROM attendance
    WHERE id = ?;
"""

COUNT_ATTENDANCE_SUMMARY = """
    SELECT
        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
        COUNT(*) AS total_count
    FROM attendance
    WHERE student_id = ?;
"""

# ---------------- WELLBEING SURVEYS ----------------
INSERT_SURVEY = """
    INSERT INTO wellbeing_surveys (student_id, stress_level, hours_slept, comments)
    VALUES (?, ?, ?, ?);
"""

GET_SURVEY_BY_ID = """
    SELECT *
    FROM wellbeing_surveys
    WHERE id = ?;
"""

GET_SURVEYS_FOR_STUDENT = """
    SELECT *
    FROM wellbeing_surveys
    WHERE student_id = ?
    ORDER BY created_at ASC;
"""

DELETE_SURVEY = """
    DELETE FROM wellbeing_surveys
    WHERE id = ?;
"""

GET_WELLBEING_AVERAGES = """
    SELECT
        AVG(stress_level) AS avg_stress,
        AVG(hours_slept) AS avg_sleep
    FROM wellbeing_surveys
    WHERE student_id = ?;
"""

# ---------------- SUBMISSIONS ----------------
INSERT_SUBMISSION = """
    INSERT INTO submissions (student_id, assignment_id, submission_date, grade)
    VALUES (?, ?, ?, ?);
"""

GET_SUBMISSION = """
    SELECT *
    FROM submissions
    WHERE id = ?;
"""

UPDATE_SUBMISSION_GRADE = """
    UPDATE submissions
    SET grade = ?
    WHERE id = ?;
"""

GET_SUBMISSIONS_FOR_STUDENT = """
    SELECT *
    FROM submissions
    WHERE student_id = ?
    ORDER BY submission_date DESC;
"""

DELETE_SUBMISSION = """
    DELETE FROM submissions
    WHERE id = ?;
"""
