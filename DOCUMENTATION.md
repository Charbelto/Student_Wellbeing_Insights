# Student Wellbeing Insights System Documentation

## 1. Project Overview

The **Student Wellbeing Insights System** is a Flask-based web application designed to track and analyze student engagement, academic performance, and mental wellbeing. It enables universities to identify at-risk students by correlating multiple data points: attendance rates, assignment submission patterns, and self-reported wellbeing metrics (stress levels, sleep hours, mood scores).

The system supports multiple user roles (Wellbeing Officers, Module Leaders, Tutors, and Students) with role-based access control. It provides automated analytics to flag students showing concerning patterns in their academic engagement and mental health.

### Key Features
- **User Authentication & Roles:** Secure login system with four distinct roles: Wellbeing Officer, Module Leader, Tutor, and Student
- **Student Management:** Centralized database of student demographics, academic information, and personal data
- **Attendance Tracking:** Record and monitor student attendance rates across multiple modules
- **Submission & Grading:** Track assignment submissions, detect late submissions, and manage grades
- **Wellbeing Surveys:** Weekly check-ins for students to self-report stress levels (1-5), sleep hours, and mood scores
- **Analytics & Reporting:** Automated identification of at-risk students based on attendance rates, stress levels, and submission patterns
- **Data Export:** Export student data to CSV format for external analysis

---

## 2. Tech Stack
- **Backend Framework:** Flask (Python 3.10+)
- **Database:** SQLite (managed via `sqlite3` with row factory for dictionary-like access)
- **Data Validation:** Pydantic BaseModel (for type safety and validation)
- **Authentication & Sessions:** Flask-Login with password hashing via Werkzeug
- **Testing:** Pytest with fixtures and mocking
- **Frontend:** Jinja2 templates with HTML/CSS
- **Additional Libraries:** werkzeug (password hashing)

---

## 3. Setup and Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Charbelto/Student_Wellbeing_Insights.git
   cd Student_Wellbeing_Insights
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database:**
   ```bash
   python -m app.main
   ```
   This will auto-initialize the SQLite database (`wellbeing.db`) on first run if it doesn't exist.

5. **Seed the Database with Default Users (Optional):**
   ```bash
   python -m app.scripts.import_data
   ```
   **Warning:** This script drops and recreates all tables. It creates default users and imports student data.

6. **Run the Application:**
   ```bash
   python -m app.main
   ```
   The server will start at `http://127.0.0.1:5000`

### Default Login Credentials (After Seeding)

| Role | Username | Password |
|------|----------|----------|
| Wellbeing Officer | `officer` | `admin123` |
| Module Leader | `leader` | `lead123` |
| Tutor | `tutor` | `tutor123` |

---

## 4. Database Schema

The SQLite database `wellbeing.db` contains 10 core tables with relational dependencies:

### Users Table
- **`users`** - Authentication and role management
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `username` (TEXT UNIQUE NOT NULL)
  - `password_hash` (TEXT NOT NULL) - Werkzeug hashed passwords
  - `role` (TEXT NOT NULL) - One of: `wellbeing_officer`, `module_leader`, `tutor`, `student`

---

## 5. Application Architecture

The application follows a **Service-Layer Pattern** to separate business logic from HTTP routes, ensuring clean code organization and testability.

### Directory Structure
```
app/
├── __init__.py              # Flask app factory (create_app)
├── main.py                  # Entry point and server startup
├── auth_routes.py           # Authentication routes (login/logout)
├── routes.py                # Main application routes (students, attendance, submissions, etc.)
├── database/
│   ├── __init__.py
│   ├── connection.py        # SQLite connection management and adapters
│   ├── models.py            # Pydantic models (User, Student, Survey, etc.)
│   ├── queries.py           # All SQL statements (centralized)
│   ├── schema.sql           # Database schema creation
│   └── __pycache__/
├── services/
│   ├── __init__.py
│   ├── student_service.py   # Student CRUD operations
│   ├── attendance_service.py # Attendance tracking
│   ├── wellbeing_service.py # Survey and wellbeing data
│   ├── submission_service.py # Assignment submission tracking
│   ├── user_service.py      # User authentication and management
│   ├── analytics_service.py # At-risk student identification
│   └── __pycache__/
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Home/dashboard
│   ├── login.html           # Login page
│   ├── students.html        # Student list and management
│   ├── dashboard.html       # Individual student wellbeing dashboard
│   ├── officer_dashboard.html # Wellbeing officer at-risk students view
│   ├── attendance.html      # Attendance records per student
│   └── submissions.html     # Submission records per student
├── utils/
│   ├── __init__.py
│   ├── helpers.py           # General utility functions
│   ├── validators.py        # Input validation helpers
│   └── __pycache__/
└── scripts/
    ├── import_data.py       # Database seeding script
    └── __pycache__/

tests/
├── __init__.py
├── conftest.py              # Pytest fixtures (db_setup, services)
├── test_analytics.py        # Analytics service tests
├── test_attendance.py       # Attendance service tests
├── test_attendance_routes.py # Attendance route tests
├── test_auth.py             # Authentication tests
├── test_database.py         # Database connection tests
├── test_routes.py           # Main route tests
├── test_student_routes.py   # Student route tests
├── test_student_service.py  # Student service tests
├── test_submission_routes.py # Submission route tests
├── test_submissions.py      # Submission service tests
└── test_wellbeing.py        # Wellbeing service tests
```

### Key Services

#### 1. **StudentService** (`app/services/student_service.py`)
Manages student creation, retrieval, and updates.

**Key Methods:**
- `create_student(name, student_id, degree_id, ...)` - Create new student record
- `get_student(student_id)` - Retrieve single student by ID
- `get_all_students()` - Retrieve all students with names
- `_map_row_to_student(row)` - Convert database row to Student model

#### 2. **AttendanceService** (`app/services/attendance_service.py`)
Tracks attendance for students across modules.

**Key Methods:**
- `record_attendance(student_id, module_id)` - Mark student present
- `record_absence(student_id, module_id)` - Mark student absent
- `get_student_attendance(student_id)` - Get all attendance records for student
- `get_attendance_rate(student_id)` - Get overall attendance percentage
- `update_attendance(student_id, module_id, total_sessions, attended_sessions, attendance_rate)` - Update record

#### 3. **WellbeingService** (`app/services/wellbeing_service.py`)
Manages student wellbeing survey submissions.

**Key Methods:**
- `submit_survey(student_id, week, stress_level, hours_slept, mood_score)` - Record weekly survey (stress 1-5)
- `get_student_history(student_id)` - Get all surveys for a student
- `delete_survey(student_id, week)` - Remove survey entry
- `get_all_surveys()` - Get all surveys (for analytics)

#### 4. **SubmissionService** (`app/services/submission_service.py`)
Handles assignment submission and grading.

**Key Methods:**
- `submit_assignment(...)` - Record submission with deadline/submitted times
- `grade_submission(submission_id, mark)` - Assign mark to submission
- `get_student_submissions(student_id)` - Get all submissions for student

#### 5. **UserService** (`app/services/user_service.py`)
Manages user authentication and authorization.

**Key Methods:**
- `create_user(username, password, role)` - Create user with hashed password
- `verify_password(username, password)` - Authenticate user
- `get_user_by_username(username)` - Retrieve user by username
- `get_user_by_id(user_id)` - Retrieve user by ID (for Flask-Login)

#### 6. **AnalyticsService** (`app/services/analytics_service.py`)
Provides data analysis and at-risk student identification.

**Key Methods:**
- `identify_at_risk_students()` - Returns list of at-risk students with reasons:
  - Attendance < 70% (absence rate > 30%)
  - Average stress level ≥ 4.0
- `get_student_wellbeing_summary(student_id)` - Aggregated metrics (attendance, stress, sleep, mood)
- `get_student_wellbeing_history(student_id, limit=30)` - Time-series survey data

---

## 6. Authentication & Authorization

### Login System
- Uses **Flask-Login** for session management
- Passwords hashed with **werkzeug.security** (`generate_password_hash`, `check_password_hash`)
- User loader configured in `app/__init__.py`

### User Roles
Four distinct roles with different access levels:

| Role | Access Level | Key Permissions |
|------|--------------|-----------------|
| **Wellbeing Officer** | Highest | Create/edit students, view all wellbeing data, identify at-risk students, export data, see sensitive medical info |
| **Module Leader** | Medium | View student list, attendance, submissions for their modules |
| **Tutor** | Medium | Record attendance, grade submissions, view basic student info |
| **Student** | Lowest | Submit wellbeing surveys, view own data (redacted sensitive info) |

### Access Control
Routes check `current_user.role` and use `@login_required` decorator. Examples:
```python
@main_bp.route('/officer_dashboard')
@login_required
def officer_dashboard():
    if current_user.role != Role.WELLBEING_OFFICER:
        flash("Access denied.", "error")
        return redirect(url_for('main.index'))
```

---

## 7. API Routes

### Authentication Routes (`/auth`)
- `GET/POST /auth/login` - User login form and authentication
- `GET /auth/logout` - User logout (requires login)

### Main Routes (`/`)
#### Student Management
- `GET /` - Home page (redirects based on role)
- `GET /students` - View all students list
- `POST /students/add` - Create new student record
- `POST /students/delete/<student_id>` - Delete student (Officer only)

#### Attendance Tracking
- `GET /attendance/<student_id>` - View student attendance records
- `POST /attendance/add` - Record attendance (present/absent)
- `POST /attendance/update/<record_id>` - Update attendance record
- `POST /attendance/delete/<record_id>` - Delete attendance record

#### Submissions
- `GET /submissions/<student_id>` - View student submissions
- `POST /submissions/add` - Record new submission
- `POST /submissions/grade/<submission_id>` - Grade submission
- `POST /submissions/delete/<submission_id>` - Delete submission

#### Analytics & Dashboards
- `GET /dashboard` - Student wellbeing dashboard (with history charts)
- `GET /officer_dashboard` - Wellbeing Officer at-risk students view
- `POST /api/submit-survey` - Submit wellbeing survey (JSON endpoint)

#### Data Export
- `GET /export/students` - Export all students to CSV (Officer only)

---

## 8. Pydantic Models

Models are defined in `app/database/models.py` for data validation and type safety:

### Enums
- **`StressLevel`** - Enum(1-5): VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH
- **`Role`** - Enum: WELLBEING_OFFICER, MODULE_LEADER, TUTOR, STUDENT

### Data Models
- **`User`** - `id`, `username`, `password_hash`, `role` (extends Flask-Login UserMixin)
- **`Student`** - Full student profile with demographics and academic info
- **`StudentName`** - Linked name record
- **`Degree`** - Degree program
- **`Module`** - Course module with schedule/difficulty
- **`ModuleFeedback`** - Student feedback (5 questions + study hours)
- **`Attendance`** - Attendance record with rate calculation
- **`Survey`** - Wellbeing survey entry
- **`Submission`** - Assignment submission with deadline tracking
- **`RiskIndicator`** - Aggregated risk metrics

---

## 9. Testing

### Test Structure
Tests use **Pytest** with fixtures defined in `conftest.py`:
- `db_setup` - Creates isolated test database for each test
- `student_service`, `attendance_service`, etc. - Service fixtures using test DB
- Cleanup with retry logic for Windows file locks

### Test Coverage
- **test_auth.py** - User creation, password verification, retrieval
- **test_analytics.py** - Wellbeing summary, at-risk identification
- **test_attendance.py** - Attendance recording, rate calculation
- **test_wellbeing.py** - Survey submission, validation
- **test_submissions.py** - Submission tracking, grading
- **test_student_service.py** - Student CRUD operations
- **test_routes.py** - Route testing (requires Flask test client)
- **test_database.py** - Database connection and initialization

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analytics.py

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_auth.py::test_create_user
```

---

## 10. Database Queries

All SQL is centralized in `app/database/queries.py` to avoid scattering raw SQL. Key patterns:

- **User Queries**: `INSERT_USER`, `GET_USER_BY_USERNAME`, `GET_USER_BY_ID`, `UPDATE_USER`, `DELETE_USER`
- **Student Queries**: `INSERT_STUDENT`, `GET_STUDENT_BY_ID`, `GET_ALL_STUDENTS_AND_NAME`, `UPDATE_STUDENT`, etc.
- **Attendance Queries**: `GET_ATTENDANCE_FOR_STUDENT`, `GET_ATTENDANCE_RATE_FOR_STUDENT`, `UPDATE_ATTENDANCE`
- **Wellbeing Queries**: `INSERT_SURVEY`, `GET_SURVEY_FOR_STUDENT`, `AVG_WELLBEING_STATS`
- **Analytics Queries**: `AVG_STRESS_STAT`, `GET_ATTENDANCE_RATE_FOR_STUDENT`

---

## 11. Key Features Explained

### At-Risk Student Identification
The `AnalyticsService.identify_at_risk_students()` flags students based on:
1. **High Absenteeism**: Absence rate > 30% (attendance < 70%)
2. **High Stress**: Average stress level ≥ 4.0 (on 1-5 scale)

Returns list with student info, flagged metrics, and reasons for concern.

### Attendance Tracking
- Records per student per module
- Tracks: total sessions, attended sessions, calculated attendance_rate
- Used to identify disengagement patterns

### Wellbeing Surveys
- Weekly submissions (stress 1-5, sleep hours, mood)
- Privacy-aware: Wellbeing Officers see all data, others see redacted versions
- Time-series data for trend analysis

### Role-Based Data Access
- **Wellbeing Officer**: Full access including medical info, all metrics
- **Module Leaders/Tutors**: Module-specific data, no medical info
- **Students**: Can only submit surveys, view own basic dashboard
- System automatically redacts sensitive fields based on role

---

## 12. Deployment Considerations

### Security
- Change `app.config['SECRET_KEY']` in `app/__init__.py` before production
- Use environment variables for configuration
- Implement HTTPS in production
- Set up proper database backups

### Performance
- Add database indexes for frequently queried columns (student_id, module_id)
- Consider caching for analytics queries
- Implement pagination for large student lists

### Data Privacy
- Sensitive fields (medical_information, disabilities) should be encrypted at rest
- Implement audit logging for data access
- Comply with GDPR/relevant data protection regulations

---

## 13. File Dependencies

### Critical Files
- `app/database/schema.sql` - Must exist for database initialization
- `requirements.txt` - Lists all dependencies
- `pyproject.toml` - Project metadata and build config

### Configuration
- Database name: `wellbeing.db` (SQLite in project root)
- Templates: Located in `app/templates/`
- Default roles and permissions in code (can be extended to database)

---

## 14. Common Issues & Troubleshooting

### Database Lock Issues (Windows)
- Tests use unique filenames (`test_wellbeing_*.db`) to avoid locks
- Cleanup includes retry logic (up to 10 attempts)

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Database Reset
```bash
# Delete the database and restart app
rm wellbeing.db
python -m app.main
```

### Import Script Fails
Ensure `app/database/PAI_dataset.xlsx` exists or modify `app/scripts/import_data.py`

---

## 15. Contributing Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints in function signatures
- Keep functions focused and under 50 lines when possible

### Adding Features
1. Add Pydantic model in `app/database/models.py` if new data type
2. Add SQL queries to `app/database/queries.py`
3. Create/update service in `app/services/`
4. Add route in `app/routes.py` or new blueprint
5. Write tests in `tests/`
6. Update templates in `app/templates/`

### Testing
- Write tests for all new services
- Aim for >80% code coverage
- Use fixtures for database setup

---

## 16. Future Enhancements

Potential features for future development:
- Email notifications for at-risk students
- Predictive modeling for early intervention
- Mobile app for survey submissions
- Real-time dashboard analytics
- Integration with university learning management system (LMS)
- Graph visualizations (stress trends, attendance patterns)
- Advanced filtering and search capabilities
- Multi-language support
- API for third-party integrations