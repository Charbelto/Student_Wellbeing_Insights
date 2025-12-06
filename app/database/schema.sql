DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS wellbeing_surveys;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT,
    degree_name TEXT,
    year INTEGER,
    medical_info TEXT,
    disabilities TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    status TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE wellbeing_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    stress_level INTEGER NOT NULL,
    hours_slept REAL NOT NULL,
    comments TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assignment_id TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    grade REAL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
