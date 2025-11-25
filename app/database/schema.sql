DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS wellbeing_surveys;
DROP TABLE IF EXISTS submissions;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id TEXT UNIQUE, -- e.g. u2554630
    name TEXT, -- We might mock this or use ID
    email TEXT,
    degree_name TEXT,
    year INTEGER,
    medical_info TEXT,
    disabilities TEXT,
    commute_type TEXT,
    avg_commute_time_min REAL,
    avg_screen_time_hours REAL
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, -- Internal FK
    course_id TEXT NOT NULL,
    status TEXT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE wellbeing_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, -- Internal FK
    date DATE NOT NULL,
    stress_level INTEGER NOT NULL,
    hours_slept REAL NOT NULL,
    comments TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, -- Internal FK
    assignment_id TEXT NOT NULL,
    submission_date TIMESTAMP NOT NULL,
    grade REAL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);
