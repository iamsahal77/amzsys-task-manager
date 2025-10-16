# Daily Task Tracker(Flask + sqlite)

## 🌐 Deployed In Render 

Level up your daily productivity with a clean, modern Flask app. This doc gives you a fast path to run it locally (on any OS), plus highlights of challenges and extra features added during the build.

## 🚀 Quick Start (Local)

### Windows (PowerShell)

```powershell
cd "C:\Users\user\Desktop\web dev\task_management"
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

### macOS/Linux (bash/zsh)

```bash
cd "~/Desktop/web dev/task_management"  # adjust if needed
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open: http://127.0.0.1:5000

## ➕ Features

- Add, edit, delete tasks
- Mark complete/incomplete
- Categories and filters
- Priority (Low/Medium/High) with color badges
- Due dates with overdue/remaining days indicator
- Search and sort (created, priority, due date, title)
- Progress bar, and "done today" stat
- Dark/Light theme toggle (persists via localStorage)
- Bootstrap 5 UI + subtle animations

## 🔧 Troubleshooting

- Port already in use: stop the other process or run `flask run -p 5001`.
- venv activation issues: ensure correct shell (`.venv/Scripts/Activate` on Windows, `source .venv/bin/activate` on macOS/Linux).
- SQLite lock: close other processes that have the DB open (e.g., editors) and retry.
