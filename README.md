# Daily Task Tracker (Flask + SQLite)

A modern daily task tracker with categories, priorities, due dates, filters/search/sort, progress stats, and dark mode.

## Features

- Add, edit, delete tasks
- Mark complete/incomplete
- Categories and filters
- Priority (Low/Medium/High) with color badges
- Due dates with overdue/remaining days indicator
- Search and sort (created, priority, due date, title)
- Progress bar, and "done today" stat
- Dark/Light theme toggle (persists via localStorage)
- Bootstrap 5 UI + subtle animations

## Tech

- Flask, Jinja2
- SQLite (file: `tasks.db` auto-created/migrated)
- Bootstrap 5

## Setup (Windows PowerShell)

```powershell
cd "C:\Users\user\Desktop\web dev\task_management"
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# (optional) set a stronger secret key
$env:FLASK_SECRET_KEY = "change-this-secret"

# Run
python app.py
```

Open `http://127.0.0.1:5000`.

## Notes

- Schema upgrades are automatic on start (new columns added if missing): `category`, `priority`, `due_date`, `completed_at`.
- Use the filters and search at the top of the list to narrow results.
- Theme toggle button in the dashboard persists your preference.
