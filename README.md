Student Wellbeing Insights (Flask + SQLite)
==========================================

A role-based wellbeing and engagement dashboard for university staff. It imports the provided `PAI_finalised.xlsx`, flags at-risk students, enforces privacy for sensitive fields, and offers analytics plus CSV exports.

Quick Start
-----------
```bash
cd "C:\Users\Charbel\Desktop\New folder (9)"
pip install -r requirements.txt
python -m app.main
# open http://127.0.0.1:5000
```

Seeded Accounts (auto on startup)
---------------------------------
- Wellbeing Officer: `officer / officer123`
- Tutor: `tutor / tutor123`
- Module Leader: `leader / lead123`

Data Import
-----------
- On first run (or when `students` has ≤1 rows), imports `app/database/PAI_finalised.xlsx`.
- Sheets ingested (case-insensitive): `students`, `student names`, `degrees`, `modules`, `submissions`, `module feedback`, `risk indicators`, `survey`, `attendance`.
- Names come from “student names”. If missing or pandas/openpyxl unavailable, a demo student is seeded.
- To force re-import: delete `wellbeing.db` and restart.

Features
--------
- RBAC: Officer, Tutor, Module Leader; medical/disability fields are officer-only.
- CRUD: students, attendance, submissions; wellbeing surveys.
- Risk: flags High/Medium from risk table, avg stress ≥4, late submissions >2; detailed CSV export.
- Analytics: Chart.js (stress trend, attendance vs mark); embedded PNGs on officer dashboard.
- Lists: paginated students, at-risk, modules, submissions, attendance, feedback, risks.
- User admin (officer): add/update/delete users (roles, optional password reset).
- Exports: risk (detailed), students CSV.
- Navigation: primary links + “More” dropdown; click to toggle, click outside to close.

Key Pages
---------
- `/` Home
- `/dashboard?student_id=...` Student dashboard (profile, lifestyle, stats, charts, survey submit)
- `/students` Students (paginated, actions to dashboard/attendance/submissions)
- `/attendance/<student_id>` per-student attendance
- `/submissions/<student_id>` per-student submissions
- `/officer_dashboard` At-risk cards, KPIs, charts (officer)
- `/analytics` Chart.js trend & scatter
- Global tables: `/modules`, `/submissions/all`, `/attendance/all`, `/feedback/all`, officer-only `/risk/all`
- User admin: `/users` (officer)
- Exports: `/export/risk`, `/export/students`

Architecture (key files)
------------------------
- `app/main.py` – app entry, seeding (users + Excel import)
- `app/routes.py` – routes, RBAC, pagination helpers, exports
- `app/services/*` – business logic (students, attendance, submissions, wellbeing, analytics, users)
- `app/templates/*` – Tailwind-based UI
- `app/database/schema.sql` – SQLite schema (FK enabled)
- `app/database/PAI_finalised.xlsx` – source data
- `tests/` – pytest suite

Run Tests
---------
```bash
cd "C:\Users\Charbel\Desktop\New folder (9)"
pytest -q
```

Requirements
------------
Listed in `requirements.txt`:
```
pytest
pydantic
flask
flask_login
bcrypt
matplotlib
pandas
openpyxl
```

