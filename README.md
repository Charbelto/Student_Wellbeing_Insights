Student Wellbeing Insights (Flask + SQLite)
==========================================

A role-based wellbeing and engagement dashboard for university staff. It ingests the provided `PAI_finalised.xlsx`, flags at-risk students, enforces privacy for sensitive fields, and offers analytics plus CSV exports.

Contents
--------
- Quick Start
- Seeded Accounts
- Data Import (Excel)
- Features & Functional Requirements
- UI / Navigation Map
- Code Skeleton
- Architecture & Key Files
- Testing
- Operational Notes & Tips

Quick Start
-----------
```bash
pip install -r requirements.txt
python -m app.main
# open http://127.0.0.1:5000
```

Seeded Accounts (auto on startup)
---------------------------------
- Wellbeing Officer: `officer / officer123`
- Tutor: `tutor / tutor123`
- Module Leader: `leader / lead123`

Data Import (Excel)
-------------------
- On first run (or when `students` has ≤1 rows), imports `app/database/PAI_finalised.xlsx`.
- Sheets ingested (case-insensitive): `students`, `student names`, `degrees`, `modules`, `submissions`, `module feedback`, `risk indicators`, `survey`, `attendance`.
- Names come from “student names”. If missing or pandas/openpyxl unavailable, a demo student is seeded.
- To force a fresh import: delete `wellbeing.db` and restart.

Features & Functional Requirements
----------------------------------
- RBAC: Officer, Tutor, Module Leader; medical/disability fields are officer-only.
- CRUD: students, attendance, submissions; wellbeing surveys.
- Risk logic: High/Medium from risk table, avg stress ≥4, late submissions >2; officer CSV export with full metrics.
- Privacy: non-officers see redacted sensitive fields; risk and user admin are officer-only.
- Analytics: Chart.js (stress trend, attendance vs mark); embedded PNGs on officer dashboard.
- Lists & pagination: students, at-risk, modules, submissions, attendance, feedback, risks (sliding window pagination).
- User admin (officer): add/update/delete users (roles; optional password reset).
- Exports: risk (detailed), students CSV.
- Navigation: main links plus “More” dropdown (modules, submissions, attendance, feedback, risks, users, officer, export).

UI / Navigation Map
-------------------
- `/` Home
- `/dashboard?student_id=...` Student dashboard (profile, lifestyle, stats, charts, survey submit)
- `/students` Students (paginated; actions to dashboard/attendance/submissions)
- `/attendance/<student_id>` per-student attendance
- `/submissions/<student_id>` per-student submissions
- `/officer_dashboard` At-risk cards, KPIs, charts (officer)
- `/analytics` Chart.js trend & scatter
- Global tables: `/modules`, `/submissions/all`, `/attendance/all`, `/feedback/all`, officer-only `/risk/all`
- User admin: `/users` (officer)
- Exports: `/export/risk`, `/export/students`

Code Skeleton
-------------
- `app/main.py`
  - create_app, DB init, schema guard, Excel import, seed users (officer/tutor/leader), optional demo student
- `app/routes.py`
  - main routes, RBAC guards, pagination helper, APIs (charts, dashboard summary), exports, global listings, user admin
- `app/services/`
  - `student_service.py` CRUD + cascade delete
  - `attendance_service.py` attendance mutations/rates
  - `submission_service.py` submissions CRUD/grade
  - `wellbeing_service.py` surveys
  - `analytics_service.py` summaries, trends, risk detection
  - `user_service.py` users, hashing, resets, role updates
- `app/templates/`
  - Tailwind-based pages: base, login, index, students, dashboard, attendance, submissions, officer_dashboard, analytics, modules, submissions_all, attendance_all, feedback_all, risk_all, users
- `app/database/`
  - `schema.sql` schema (FK on)
  - `PAI_finalised.xlsx` source data
  - `queries.py` SQL statements
- `tests/` pytest suite and fixtures

Architecture & Key Files
------------------------
- `app/main.py` – entrypoint, seeding (users + Excel)
- `app/routes.py` – routing, RBAC, exports, pagination
- `app/services/*` – business logic
- `app/templates/*` – UI
- `app/database/schema.sql` – schema
- `tests/` – automated tests

Testing
-------
```bash
pytest -q
```

Operational Notes & Tips
------------------------
- “More” menu toggles on click; closes when clicking outside.
- Attendance rates normalize to 0–100% even if stored as fractions.
- Risk export includes detailed metrics (stress, late submissions, avg/min/max mark, reasons).
- If Excel import is skipped (table already populated), delete `wellbeing.db` to force a clean import.***

