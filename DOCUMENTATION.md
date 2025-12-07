# Student Wellbeing Insights System Documentation

## 1. Project Overview
The **Student Wellbeing Insights System** is a Flask-based web application designed to track and analyze student engagement, academic performance, and mental wellbeing. It allows universities to identify "at-risk" students by correlating attendance, submission deadlines, and self-reported wellbeing metrics (stress, sleep, mood).

### Key Features
- **User Authentication & Roles:** Secure access for Wellbeing Officers, Module Leaders, Tutors, and Students.
- **Student Management:** centralized database of student demographics and academic details.
- **Attendance Tracking:** Monitor student attendance across modules.
- **Submission & Grading:** Track assignment submissions, lateness, and marks.
- **Wellbeing Surveys:** Weekly check-ins for students to report stress levels, sleep hours, and mood.
- **Analytics Dashboard:** Automated identification of at-risk students based on configurable thresholds (e.g., high stress, low attendance).

---

## 2. Tech Stack
- **Backend Framework:** Flask (Python)
- **Database:** SQLite (Managed via `sqlite3` and raw SQL queries)
- **Data Validation:** Pydantic Models
- **Authentication:** Flask-Login
- **Testing:** Pytest
- **Frontend:** Jinja2 Templates (HTML/CSS)

---

## 3. Setup and Installation

### Prerequisites
- Python 3.8+
- pip

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database:**
   Run the application once to auto-initialize the SQLite database if it doesn't exist, or manually run the initialization script if available. The application checks for `wellbeing.db` on startup.
   ```bash
   python -m app.main
   ```

5. **Run the Application:**
   ```bash
   python -m app.main
   ```
   The server will start at `http://127.0.0.1:5000`.

### Data Import & Seeding
The application includes a script to initialize the database with default users and import student data from an Excel file.

**To seed the database:**
```bash
python -m app.scripts.import_data
```
This script will:
1. Re-initialize the database (Warning: Drops existing tables).
2. Create default users (see below).
3. Import student data from `app/database/PAI_dataset.xlsx`.

### Default Login Credentials
After running the import script, you can log in with the following users:

| Role | Username | Password |
|------|----------|----------|
| **Wellbeing Officer** | `officer` | `admin123` |
| **Module Leader** | `leader` | `lead123` |
| **Tutor** | `tutor` | `tutor123` |

---

## 4. Database Schema

The database `wellbeing.db` consists of the following relational tables:

### Core Tables
- **`users`**: Authentication credentials and roles.
  - `id`, `username`, `password_hash`, `role`
- **`students`**: Demographic and degree information.
  - `student_id` (PK), `degree_id`, `year`, `age_band`, `domicile`, `disabilities`, etc.
- **`student_names`**: Separate table linking IDs to names.
  - `student_id`, `name`
- **`degrees`** & **`modules`**: Academic structure.
  - `degrees`: `degree_id`, `degree_name`
  - `modules`: `module_id`, `code`, `name`, `semester`, `lecture_time`, etc.

### Tracking Tables
- **`attendance`**: Records student presence in sessions.
  - `student_id`, `module_id`, `total_sessions`, `attended_sessions`, `attendance_rate`
- **`submissions`**: Assignment tracking.
  - `submission_id`, `student_id`, `module_id`, `deadline_datetime`, `submitted_datetime`, `mark`, `late` (boolean)
- **`survey`**: Weekly wellbeing data.
  - `student_id`, `week`, `stress_level` (1-5), `hours_slept`, `mood_score`
- **`module_feedback`**: Student feedback on courses.
- **`risk_indicator`**: Cached/Computed risk metrics for students.

---

## 5. Application Architecture

The application follows a Service-Layer pattern to separate business logic from HTTP routes.

### Directory Structure
```
app/
├── database/       # Database connection, models, and schema
├── services/       # Business logic (Student, Attendance, Wellbeing, Analytics)
├── templates/      # HTML frontend files
├── utils/          # Helper functions and validators
├── auth_routes.py  # Login/Logout logic
├── main.py         # App factory and entry point
└── routes.py       # Main application controllers
```

### Services
- **`UserService`**: Handles user creation, password hashing (Werkzeug), and authentication verification.
- **`StudentService`**: Manages student CRUD operations and data retrieval.
- **`AttendanceService`**: Records presence/absence and calculates attendance rates.
- **`SubmissionService`**: Handles assignment submissions, lateness checks, and grading.
- **`WellbeingService`**: Processes weekly survey data.
- **`AnalyticsService`**: Aggregates data from other services to generate summaries and identify "at-risk" students.
  - **At-Risk Logic:** Flags students with Attendance < 70% (or >30% absence) AND/OR Average Stress > 4.0.

---

## 6. API Endpoints & Routes

### Authentication (`auth_routes.py`)
- `GET/POST /login`: User login.
- `GET /logout`: User logout.

### General & Dashboard (`routes.py`)
- `GET /`: Landing page (redirects based on role).
- `GET /dashboard`: Detailed student view (Wellbeing summary, history).
- `GET /officer_dashboard`: **(Restricted)** Shows list of "At-Risk" students.

### Student Management
- `GET /students`: List all students.
- `POST /students/add`: Add a new student.
- `POST /students/delete/<id>`: Delete a student and all related data.
- `GET /export/students`: Download student data as CSV.

### Attendance
- `GET /attendance/<student_id>`: View attendance record.
- `POST /attendance/add`: Record a new attendance entry.
- `POST /attendance/update/<id>`: Update an existing record.
- `POST /attendance/delete/<id>`: Remove a record.

### Submissions
- `GET /submissions/<student_id>`: View student assignments.
- `POST /submissions/add`: Submit an assignment.
- `POST /submissions/grade/<id>`: Grade a submission.
- `POST /submissions/delete/<id>`: Delete a submission.

### API (JSON)
- `POST /api/submit-survey`: Endpoint for submitting wellbeing survey data via JSON.

---

## 7. User Roles

1. **Wellbeing Officer (`wellbeing_officer`)**:
   - Full access to dashboards.
   - Can view "At-Risk" reports.
   - Can add/delete students.
   - Can view medical info and sensitive data.
2. **Module Leader (`module_leader`)**:
   - Can view student lists.
   - Restricted from sensitive medical/wellbeing details.
3. **Tutor (`tutor`)**:
   - Standard view access.
4. **Student (`student`)**:
   - Limited access (typically to their own data, though the current implementation focuses on staff views).

---

## 8. Testing

The project uses `pytest` for testing. Tests are located in the `tests/` directory.

**Running Tests:**
```bash
pytest
```
This will run all test suites, checking services, database integrity, and route responses.

