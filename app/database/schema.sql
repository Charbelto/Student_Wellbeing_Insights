DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS student_names;
DROP TABLE IF EXISTS degrees;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS module_feedback;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS survey;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS risk_indicator;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    degree_id INTEGER NOT NULL, -- Internal FK
    degree_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    age_band TEXT NOT NULL,
    domicile TEXT NOT NULL,
    go_home_frequency TEXT,
    extracurricular_per_week INTEGER,
    avg_commute_time_min INTEGER,
    avg_screen_time_hours INTEGER,
    commute_type TEXT,
    medical_information TEXT,
    disabilities TEXT,
    FOREIGN KEY (degree_id) REFERENCES degrees (degree_id)
);

CREATE TABLE student_names (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);

CREATE TABLE degrees (
    degree_id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_name TEXT NOT NULL
);

CREATE TABLE modules (
    module_id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_id INTEGER NOT NULL, -- Internal FK
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    semester INTEGER NOT NULL,
    lecture_day TEXT NOT NULL,
    lecture_time TEXT NOT NULL,
    difficulty_level TEXT,
    FOREIGN KEY (degree_id) REFERENCES degrees (degree_id)
);

CREATE TABLE module_feedback(
    feedback_id TEXT NOT NULL,
    student_id TEXT NOT NULL, -- Internal FK
    module_id INTEGER NOT NULL, -- Internal FK
    engaging_content INTEGER NOT NULL,
    comfortable_asking_questions INTEGER NOT NULL,
    pace_rating	INTEGER NOT NULL,
    prepared_for_exams INTEGER NOT NULL,
    hours_outside_class INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (module_id) REFERENCES modules (module_id)
);

-- update this to match spreadsheet
CREATE TABLE attendance (
    student_id TEXT NOT NULL, -- Internal FK
    module_id INTEGER NOT NULL,
    total_sessions INTEGER NOT NULL,
    attended_sessions INTEGER NOT NULL,
    attendance_rate REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);

CREATE TABLE survey (
    student_id INTEGER NOT NULL, -- Internal FK
    week INTEGER NOT NULL,
    stress_level INTEGER NOT NULL,
    hours_slept INTEGER NOT NULL,
    mood_score INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);

CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY,
    student_id TEXT NOT NULL, -- Internal FK
    module_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    deadline_datetime DATETIME NOT NULL,
    submitted_datetime DATETIME NOT NULL,
    early_late_submissions INTEGER NOT NULL,
    mark REAL,
    late BOOLEAN NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (module_id) REFERENCES modules (module_id)
);

CREATE TABLE risk_indicator(
    student_id TEXT PRIMARY KEY, -- Internal FK
    avg_stress REAL NOT NULL,
    late_submissions INTEGER NOT NULL,
    avg_mark REAL NOT NULL,
    min_mark REAL NOT NULL,
    max_mark REAL NOT NULL,
    risk_level TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);
