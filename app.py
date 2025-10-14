"""Daily Task Tracker (Flask + SQLite)

This module implements a small productivity app with:
- CRUD for tasks
- Categories, priorities, due dates
- Filters, search, sort, and progress stats
- Flash toasts and a polished Bootstrap UI

The database schema is initialized and migrated idempotently on each request.
"""

import os
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, g

# App setup
app = Flask(__name__)
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "tasks.db")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")


# ----------------------------
# Database helpers and schema
# ----------------------------

def get_db() -> sqlite3.Connection:
    """Return a request-scoped SQLite connection with Row factory."""
    if "db" not in g:
        conn = sqlite3.connect(app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(e=None) -> None:
    """Close the request-scoped DB connection if it exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.teardown_appcontext
def teardown_db(exception):
    """Flask teardown hook to ensure DB connection is closed."""
    close_db()


def _column_exists(db: sqlite3.Connection, table: str, column: str) -> bool:
    """Return True if a column exists on a given table (SQLite PRAGMA-based)."""
    cur = db.execute(f"PRAGMA table_info({table})")
    for row in cur.fetchall():
        if row[1] == column:
            return True
    return False


def init_db() -> None:
    """Create base table and migrate new columns in an idempotent fashion."""
    db = get_db()
    # Base table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        """
    )
    # Schema extensions (idempotent)
    if not _column_exists(db, "tasks", "category"):
        db.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT ''")
    if not _column_exists(db, "tasks", "priority"):
        db.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
    if not _column_exists(db, "tasks", "due_date"):
        db.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
    if not _column_exists(db, "tasks", "completed_at"):
        db.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
    db.commit()


# ----------------------------
# CRUD utilities and queries
# ----------------------------

def create_task(title: str, description: str, category: str, priority: str, due_date: str | None) -> None:
    """Insert a new task with the provided fields."""
    db = get_db()
    db.execute(
        """
        INSERT INTO tasks (title, description, status, created_at, category, priority, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title.strip(),
            description.strip(),
            0,
            datetime.utcnow().isoformat(),
            (category or "").strip(),
            (priority or "Medium").strip(),
            (due_date or None),
        ),
    )
    db.commit()


def _row_to_task_dict(row: sqlite3.Row) -> dict:
    """Convert a Row to a dict and derive helper flags (overdue, days left)."""
    task = dict(row)
    due_iso = task.get("due_date")
    task["is_overdue"] = False
    task["days_left_display"] = None
    if due_iso:
        try:
            # Accept YYYY-MM-DD or full ISO
            d = date.fromisoformat(due_iso[:10])
            today = date.today()
            delta = (d - today).days
            if delta < 0 and not task.get("status"):
                task["is_overdue"] = True
            task["days_left_display"] = delta
        except Exception:
            task["days_left_display"] = None
    return task


def _query_tasks(filters: dict, sort: str) -> list[dict]:
    """Return tasks matching filters and sort order.

    filters: {"status": str|"", "category": str|"", "q": str|""}
    sort: one of "created" (default), "priority", "due_date", "title"
    """
    db = get_db()
    where = []
    params: list = []

    # Status filter
    status = filters.get("status")
    if status == "completed":
        where.append("status = 1")
    elif status == "pending":
        where.append("status = 0")

    # Category filter
    category = filters.get("category")
    if category:
        where.append("category = ?")
        params.append(category)

    # Text search
    q = filters.get("q")
    if q:
        where.append("(title LIKE ? OR description LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    # Sorting
    order_by = "created_at DESC"
    if sort == "priority":
        # Custom order: High > Medium > Low, then created_at desc
        order_by = "CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, created_at DESC"
    elif sort == "due_date":
        order_by = "CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date ASC"
    elif sort == "title":
        order_by = "title COLLATE NOCASE ASC"

    cur = db.execute(f"SELECT * FROM tasks {where_sql} ORDER BY {order_by}", params)
    rows = cur.fetchall()
    return [_row_to_task_dict(r) for r in rows]


def get_task(task_id: int) -> sqlite3.Row | None:
    """Fetch a single task by id (or None)."""
    db = get_db()
    cur = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return cur.fetchone()


def update_task(task_id: int, title: str, description: str, category: str, priority: str, due_date: str | None) -> None:
    """Update a task's editable fields."""
    db = get_db()
    db.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, category = ?, priority = ?, due_date = ?
        WHERE id = ?
        """,
        (title.strip(), description.strip(), (category or "").strip(), (priority or "Medium").strip(), (due_date or None), task_id),
    )
    db.commit()


def delete_task(task_id: int) -> None:
    """Delete a task by id."""
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()


def set_task_status(task_id: int, completed: bool) -> None:
    """Toggle completion and set/reset completed_at timestamp."""
    db = get_db()
    completed_at = datetime.utcnow().isoformat() if completed else None
    db.execute(
        "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
        (1 if completed else 0, completed_at, task_id),
    )
    db.commit()


# ----------------------------
# Routes
# ----------------------------
@app.before_request
def ensure_db():
    """Ensure the DB schema exists and migrations are applied before each request."""
    init_db()


@app.get("/")
def index():
    """Render the task list with filters, search, sort, and summary stats."""
    # Filters from query params
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    q = request.args.get("q", "")
    sort = request.args.get("sort", "created")

    tasks = _query_tasks({"status": status, "category": category, "q": q}, sort)

    # Stats
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status"))
    progress_pct = int((completed / total) * 100) if total else 0

    # Today stats (based on completed_at date)
    today_str = date.today().isoformat()
    done_today = 0
    for t in tasks:
        ca = t.get("completed_at")
        if ca and ca[:10] == today_str:
            done_today += 1

    # Distinct categories for filter UI
    db = get_db()
    cats = [r[0] for r in db.execute("SELECT DISTINCT category FROM tasks WHERE category IS NOT NULL AND category != '' ORDER BY category").fetchall()]

    return render_template(
        "index.html",
        tasks=tasks,
        filters={"status": status, "category": category, "q": q, "sort": sort},
        stats={"total": total, "completed": completed, "progress_pct": progress_pct, "done_today": done_today},
        categories=cats,
    )


@app.post("/add")
def add():
    """Handle new task creation from the add form."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    priority = request.form.get("priority", "Medium").strip()
    due_date = request.form.get("due_date") or None

    if not title:
        flash("Title is required", "warning")
        return redirect(url_for("index"))

    create_task(title, description, category, priority, due_date)
    flash("Task added successfully", "success")
    return redirect(url_for("index"))


@app.get("/edit/<int:task_id>")
def edit(task_id: int):
    """Render the edit form for a specific task."""
    task = get_task(task_id)
    if task is None:
        flash("Task not found", "danger")
        return redirect(url_for("index"))
    return render_template("edit.html", task=dict(task))


@app.post("/edit/<int:task_id>")
def update(task_id: int):
    """Persist edits from the edit form for a specific task."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    priority = request.form.get("priority", "Medium").strip()
    due_date = request.form.get("due_date") or None

    if not title:
        flash("Title is required", "warning")
        return redirect(url_for("edit", task_id=task_id))

    update_task(task_id, title, description, category, priority, due_date)
    flash("Task updated successfully", "success")
    return redirect(url_for("index"))


@app.post("/delete/<int:task_id>")
def remove(task_id: int):
    """Delete a task and redirect to the list view."""
    delete_task(task_id)
    flash("Task deleted", "info")
    return redirect(url_for("index"))


@app.post("/toggle/<int:task_id>")
def toggle(task_id: int):
    """Toggle a task's completion status and redirect to the list view."""
    task = get_task(task_id)
    if task is None:
        flash("Task not found", "danger")
        return redirect(url_for("index"))
    set_task_status(task_id, completed=(not bool(task["status"])))
    flash("Task status updated", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Dev server
    app.run(debug=True)
