import json
import os
import sqlite3
from passlib.context import CryptContext


def sync(db_path: str = "tasks.db", json_path: str = "db.json") -> None:
    if not os.path.exists(json_path):
        print(f"{json_path} not found")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    # Create users table if missing
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT
        )
        """
    )

    # Create tasks table if missing
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )
        """
    )

    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    # Insert users
    for u in data.get("users", []):
        cur.execute("SELECT id FROM users WHERE id = ?", (u["id"],))
        if cur.fetchone():
            continue
        hashed = pwd_context.hash("password123")
        cur.execute(
            "INSERT INTO users (id, name, password_hash) VALUES (?, ?, ?)",
            (u["id"], u["name"], hashed),
        )

    # Insert tasks
    for t in data.get("tasks", []):
        cur.execute("SELECT id FROM tasks WHERE id = ?", (t["id"],))
        if cur.fetchone():
            continue
        cur.execute(
            "INSERT INTO tasks (id, title, owner_id) VALUES (?, ?, ?)",
            (t["id"], t["title"], t["owner_id"]),
        )

    conn.commit()
    print("Synced JSON into", db_path)
    conn.close()


if __name__ == "__main__":
    sync("tasks.db", "db.json")
