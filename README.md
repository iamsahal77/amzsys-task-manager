# Daily Task Tracker – Quick Guide & Notes

## 🌐 Deploy to Render (free)

1. Push this folder to a GitHub repository (public or private).
2. Files added for you:
   - `Procfile` → runs the app with `gunicorn app:app`
   - `requirements.txt` → includes `gunicorn`
   - `render.yaml` → one-click blueprint (optional)
   - `runtime.txt` → pins Python version
3. Option A – Blueprint deploy (fastest):
   - In Render: New → Blueprint → Connect repository → pick this repo
   - Render reads `render.yaml` and sets up the service automatically
   - It will generate a `FLASK_SECRET_KEY` for you
4. Option B – Manual Web Service:
   - New → Web Service → Connect repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variable: `FLASK_SECRET_KEY` with any strong value
5. Click Deploy → wait for build → open your Render URL.

Note on SQLite: Render’s free filesystem is ephemeral; `tasks.db` may reset after deploy/idle. For durable data, switch to a free Postgres (e.g., Neon) and I can adapt the app.

---

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
