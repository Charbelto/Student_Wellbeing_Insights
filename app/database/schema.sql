DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS wellbeing_surveys;
DROP TABLE IF EXISTS submissions;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    status TEXT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE wellbeing_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    stress_level INTEGER NOT NULL,
    hours_slept REAL NOT NULL,
    comments TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assignment_id TEXT NOT NULL,
    submission_date TIMESTAMP NOT NULL,
    grade REAL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);
