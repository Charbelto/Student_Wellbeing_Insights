# Placeholder for SQL queries
class Queries:
    # -------------- STUDENTS --------------
    INSERT_STUDENT = """ 
        INSERT INTO students (
            student_id, degree_id, degree_name, year, age_band, domicile, go_home_frequency, extracurricular_per_week, avg_commute_time_min, avg_screen_time_hours, commute_type, medical_information, disabilities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    GET_STUDENT_BY_ID = """
        SELECT * 
        FROM students 
        WHERE student_id = ?;
    """
    
    GET_STUDENTS_BY_DEGREE = """
        SELECT * 
        FROM students 
        WHERE degree_id = ?
        OR degree_name = ?;
    """
    
    GET_STUDENTS_BY_MEDICAL_INFO = """
        SELECT * 
        FROM students 
        WHERE medical_information != "None";
    """
    
    GET_STUDENTS_BY_DISABILITY = """
        SELECT * 
        FROM students 
        WHERE disabilities != "None";
    """
    
    GET_ALL_STUDENTS = """
        SELECT * 
        FROM students;
    """

    UPDATE_STUDENT = """
        UPDATE students SET
            student_id = ?, degree_id = ?, degree_name, = ? year = ?, age_band = ?, domicile = ?, go_home_frequency = ?, extracurricular_per_week = ?, avg_commute_time_min = ?, avg_screen_time_hours = ?, commute_type = ?, medical_information = ?, disabilities = ?
        WHERE student_id = ?;
    """

    DELETE_STUDENT = """
        DELETE FROM students 
        WHERE student_id = ?;
    """

    STUDENTS_BY_DEGREE = """
        SELECT
            degree_name,
            COUNT(*) AS count
        FROM students
        GROUP BY degree_name;
    """

    AVG_COMMUTE_BY_DEGREE = """
        SELECT
            degree_name,
            AVG(avg_commute_time_min) AS avg_commute
        FROM students
        GROUP BY degree_name;
    """

    SCREEN_TIME_DISTRIBUTION = """
        SELECT
            avg_screen_time_hours,
            COUNT(*) as count
        FROM students
        GROUP BY avg_screen_time_hours
        ORDER BY avg_screen_time_hours;
    """

    # -------------- STUDENT NAMES --------------
    INSERT_NAME = """
        INSERT INTO student_names (student_id, name)
        VALUES (?, ?);
    """
    
    DELETE_NAME = """
        DELETE FROM student_names 
        WHERE student_id = ?;
    """
    
    UPDATE_NAME = """
        UPDATE student_names SET
            student_id = ?
            name = ?
        WHERE student_id = ?;
    """
    
    GET_NAME = """
        SELECT *
        FROM student_names
        WHERE student_id = ?;
    """
    
    GET_ALL_NAMES = """
        SELECT * 
        FROM student_names;
    """

    # -------------- DEGREES --------------
    INSERT_DEGREE = """
        INSERT INTO degrees (degree_name)
        VALUES (?);
    """
    
    DELETE_DEGREE = """
        DELETE FROM degrees 
        WHERE degree_id = ?;
    """
    
    UPDATE_DEGREE = """
        UPDATE degrees SET
            degree_name = ?
        WHERE degree_id = ?;
    """
    
    GET_DEGREE = """
        SELECT *
        FROM degrees
        WHERE degree_id = ?;
    """
    
    GET_ALL_DEGREES = """
        SELECT * 
        FROM degrees;
    """
    
    # -------------- MODULES --------------
    INSERT_MODULE = """
        INSERT INTO modules (
            module_id, degree_id, code, name, semester, lecture_day, lecture_time, difficulty_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    DELETE_MODULE = """
        DELETE FROM modules 
        WHERE module_id = ?
            OR code = ?;
    """
    
    UPDATE_MODULE = """
        UPDATE modules SET
            module_id = ?, degree_id = ?, code = ?, name = ?, semester = ?, lecture_day = ?, lecture_time = ?, difficulty_level = ?
        WHERE module_id = ?
            OR code = ?;
    """
    
    GET_MODULE = """
        SELECT *
        FROM modules
        WHERE module_id = ?
            OR code = ?;
    """
    
    GET_ALL_MODULES_FROM_DEGREE = """
        SELECT * 
        FROM modules
        WHERE module_id = ?
            OR code = ?;
    """
    
    GET_ALL_MODULES_FROM_SEMESTER = """
        SELECT * 
        FROM modules
        WHERE module_id = ?
            OR code = ?;
    """
    
    GET_ALL_MODULES_FROM_DAY = """
        SELECT * 
        FROM modules
        WHERE module_id = ?
            OR code = ?;
    """
    
    GET_ALL_MODULES = """
        SELECT * 
        FROM modules;
    """

    # -------------- MODULE FEEDBACK --------------
    INSERT_FEEDBACK = """
        INSERT INTO module_feedback (
            feedback_id, student_id, module_id, engaging_content, comfortable_asking_questions, pace_rating, prepared_for_exams, hours_outside_class
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    DELETE_FEEDBACK = """
        DELETE FROM module_feedback 
        WHERE feedback_id = ?;
    """
    
    UPDATE_FEEDBACK = """
        UPDATE module_feedback SET
            feedback_id = ?, student_id = ?, module_id = ?, engaging_content = ?, comfortable_asking_questions = ?, pace_rating = ?, prepared_for_exams = ?, hours_outside_class = ?
        WHERE feedback_id = ?;
    """
    
    GET_FEEDBACK = """
        SELECT *
        FROM module_feedback
        WHERE feedback_id = ?;
    """
    
    GET_ALL_FEEDBACK = """
        SELECT * 
        FROM module_feedback;
    """
    
    # -------------- ATTENDANCE --------------
    INSERT_ATTENDANCE = """
        INSERT INTO attendance (
            student_id, module_id, total_sessions, attended_sessions, attendance_rate
        )
        VALUES (?, ?, ?, ?, ?);
    """
    
    DELETE_STUDENT_ATTENDANCE = """
        DELETE FROM attendance 
        WHERE student_id = ?;
    """
    
    DELETE_MODULE_ATTENDANCE = """
        DELETE FROM attendance 
        WHERE student_id = ?
            AND module_id = ?;
    """
    
    UPDATE_ATTENDANCE = """
        UPDATE attendance SET
            student_id = ?, module_id = ?, total_sessions = ?, attended_sessions = ?, attendance_rate = ?
        WHERE student_id = ?
            AND module_id = ?;
    """

    GET_ATTENDANCE_FOR_STUDENT = """
        SELECT *
        FROM attendance
        WHERE student_id = ?;
    """

    GET_ATTENDANCE_FOR_MODULE = """
        SELECT *
        FROM attendance
        WHERE module_id = ?;
    """
    
    GET_ATTENDANCE_FOR_COURSE = """
        SELECT
            degrees.degree_name,
            attendance.*
        FROM attendance
        INNER JOIN modules
        ON attendance.module_id = modules.module_id
        INNER JOIN degrees
        ON modules.degree_id = degrees.degree_id;
    """

    ATTENDANCE_PERCENTAGE_FOR_MODULE = """
        SELECT
            module_id
            (AVG(CAST(REPLACE(attendance_rate, '%', '') AS REAL)) || '%') AS avg_attendance_rate
        FROM attendance
        GROUP BY module_id;
    """

    # -------------- SURVEY --------------
    INSERT_SURVEY = """
        INSERT INTO survey (student_id, week, stress_level, hours_slept, mood_score)
        VALUES (?, ?, ?, ?, ?);
    """
    
    DELETE_SURVEY = """
        DELETE FROM survey 
        WHERE student_id = ?;
    """
    
    UPDATE_SURVEY = """
        UPDATE survey SET
            student_id = ?, week = ?, stress_level = ?, hours_slept = ?, mood_score = ?
        WHERE student_id = ?;
    """

    GET_WELLBEING_FOR_STUDENT = """
        SELECT * FROM survey
        WHERE student_id = ?
        ORDER BY week ASC;
    """

    AVG_WELLBEING_STATS = """
        SELECT 
            AVG(stress_level) AS avg_stress,
            AVG(hours_slept) AS avg_sleep
            AVG(mood_score) AS avg_mood
        FROM survey
        WHERE student_id = ?;
    """

    # -------------- SUBMISSIONS --------------
    INSERT_SUBMISSION = """
        INSERT INTO submissions (
            submission_id, student_id, module_id, semester, deadline_datetime, submitted_datetime, early_late_submissions, mark, late
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    DELETE_SUBMISSION = """
        DELETE FROM submissions 
        WHERE submission_id = ?;
    """
    
    DELETE_SUBMISSIONS_STUDENT = """
        DELETE FROM submissions 
        WHERE student_id = ?;
    """
    
    UPDATE_SUBMISSION = """
        UPDATE submissions SET
            submission_id = ?, student_id = ?, module_id = ?, semester = ?, deadline_datetime = ?, submitted_datetime = ?, early_late_submissions = ?,mark = ?, late = ?
        WHERE submission_id = ?;
    """

    GET_SUBMISSIONS_FOR_STUDENT = """
        SELECT *
        FROM submissions
        WHERE student_id = ?
        ORDER BY submission_date DESC;
    """

    GET_MARKS_FOR_STUDENT = """
        SELECT module_id, mark
        FROM submissions
        WHERE student_id = ?;
    """

    AVG_GRADE_FOR_STUDENT = """
        SELECT AVG(mark) AS avg_grade
        FROM submissions
        WHERE student_id = ?;
    """
    
    AVG_GRADE_FOR_STUDENT_MODULE = """
        SELECT AVG(mark) AS avg_grade
        FROM submissions
        WHERE student_id = ?
            AND module_id = ?;
    """
    
    LATE_PERCENTAGE = """
        SELECT
            COUNT(*) as submissions_total,
            SUM(CASE WHEN late = 'TRUE' THEN 1 ELSE 0 END) AS late_sumbissions,
            (SUM(CASE WHEN late = 'TRUE' THEN 1 ELSE 0 END) * 1.0 /COUNT(*)) * 100 AS percentage_late
        FROM submissions
        WHERE student_id = ?;
    """

    # -------------- RISK INDICATORS --------------
    INSERT_RISK = """
        INSERT INTO risk_indicator (
        
    )
        VALUES (?);
    """
    
    DELETE_RISK = """
        DELETE FROM risk_indicator 
        WHERE student_id = ?;
    """
    
    UPDATE_RISK = """
        UPDATE risk_indicator SET
             = ?
        WHERE student_id = ?;
    """
    
    GET_RISK = """
        SELECT
            student_names.name,
            risk_indicator.*
        FROM risk_indicator
        INNER JOIN student_names
        ON risk_indicator.student_id = student_names.student_id
        WHERE student_id = ?;
    """
    
    GET_HIGH_RISK = """
        SELECT
            student_names.name,
            risk_indicator.*
        FROM risk_indicator
        LEFT JOIN student_names
        ON risk_indicator.student_id = student_names.student_id
        WHERE risk_level = 'High';
    """
    
    GET_MEDIUM_RISK = """
        SELECT
            student_names.name,
            risk_indicator.*
        FROM risk_indicator
        LEFT JOIN student_names
        ON risk_indicator.student_id = student_names.student_id
        WHERE risk_level = 'High' OR 'Medium';
    """
    
    # User can input a value and all students with a stress higher than the input will be returned
    GET_STRESS_RISK = """
        SELECT
            student_names.name,
            risk_indicator.avg_stress
        FROM risk_indicator
        LEFT JOIN student_names
        ON risk_indicator.student_id = student_names.student_id
        WHERE risk_indicator.avg_stress > ?;
    """
    
    GET_ALL_RISKS = """
        SELECT * 
        FROM risk_indicator;
    """
    
    GET_ALL_RISKS_NAMES = """
        SELECT
            student_names.name,
            risk_indicator.*
        FROM risk_indicator
        LEFT JOIN student_names
        ON risk_indicator.student_id = student_names.student_id
    """

    # -------------- ANALYTICS --------------
    # Average commute time vs avg_stress by commute type - scatter
    COMMUTE_VS_AVG_STRESS = """
        SELECT
            risk_indicator.avg_stress,
            students.avg_commute_time_min,
            students.commute_type
        FROM students
        INNER JOIN risk_indicator
        ON students.student_id = risk_indicator.student_id;
    """

    # Percentage of late submissions broken down into modules/course
    PERC_LATE_BY_COURSE = """
        SELECT
            degrees.degree_name,
            submissions.late
        FROM submissions
        INNER JOIN modules
        ON submissions.module_id = modules.module_id
        INNER JOIN degrees
        ON modules.degree_id = degrees.degree_id;
    """


