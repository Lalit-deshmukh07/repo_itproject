import sqlite3
from pathlib import Path


class TaskRepository:
    def __init__(self, db_path: str = "tasks.db"):
        app_root = Path(__file__).resolve().parents[1]
        self._memory = db_path in (":memory", ":memory:")
        if self._memory:
            self._conn = sqlite3.connect(":memory:")
            self._conn.row_factory = sqlite3.Row
            self._db_path = ":memory:"
        else:
            self._conn = None
            self._db_path = Path(db_path)
            if not self._db_path.is_absolute():
                self._db_path = app_root / self._db_path
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _get_connection(self):
        if self._memory:
            return self._conn
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        with self._get_connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL)"
            )

    def list_tasks(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id, title FROM tasks ORDER BY id").fetchall()
            return [{"id": row["id"], "title": row["title"]} for row in rows]

    def get_task(self, task_id: int):
        with self._get_connection() as conn:
            row = conn.execute("SELECT id, title FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return {"id": row["id"], "title": row["title"]} if row else None

    def add_task(self, title: str):
        with self._get_connection() as conn:
            cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
            task_id = cursor.lastrowid
            return {"id": task_id, "title": title}

    def update_task(self, task_id: int, title: str):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET title = ? WHERE id = ?", (title, task_id)
            )
            if cursor.rowcount == 0:
                return None
            return self.get_task(task_id)

    def remove_task(self, task_id: int):
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
