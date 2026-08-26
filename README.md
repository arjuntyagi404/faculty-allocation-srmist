# Faculty Subject Allocation System — SRMIST

A web application to manage and allocate subjects to faculty members.

## Features
- Faculty registration (Add, Edit, Remove)
- Subject allocation (max 2 subjects per faculty)
- Individual workload viewer with timetable

## Tech Stack
- **Backend:** Python + Flask
- **Database:** SQLite (via SQLAlchemy)
- **Frontend:** HTML, CSS, Jinja2

## Setup Instructions
1. Clone the repo
   git clone https://github.com/YOUR-USERNAME/faculty-allocation-srmist.git

2. Install dependencies
   pip install -r requirements.txt

3. Run the app
   python app.py

4. Open http://localhost:5000

## CSV import

Run `python seed_database.py` for a read-only dry run. It reports source row
counts, duplicates, missing optional values, unresolved references, and
validation errors. Run `python seed_database.py --import` only after a clean
dry run. The operation is transactional, insert-only, and never drops or
overwrites existing records. Imported faculty accounts have no password hash;
an administrator must set one through `POST /faculty/reset-password/<faculty_id>`
with a JSON `password` value before that faculty member can log in. Passwords
are hashed and are never read from or written to the CSV files.
Missing faculty posts use the existing `Assistant Professor` default; missing
personal fields remain NULL. Theory allocation `batch` and `slot` values may
also remain NULL because the existing allocation schema now permits those
catalog records to be preserved without inventing timetable data.

## Team
- Your Name (your roll number)
- Teammate Name (their roll number)

## Mentor
- Prof. [Name] — SRMIST

------------------------------------------------------my corner---------

Faculty Allocation System

Backend Stack

- Flask
- SQLite
- SQLAlchemy

Completed

✓ Faculty CRUD
✓ Scheduler
✓ Timetable Builder

Pending

□ Authentication
□ Allocation CRUD
□ Docker
□ Deployment
