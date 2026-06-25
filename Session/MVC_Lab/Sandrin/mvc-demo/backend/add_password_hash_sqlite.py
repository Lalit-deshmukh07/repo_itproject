import sqlite3
from passlib.context import CryptContext


def ensure_password_hash(db_path: str = "tasks.db") -> None:
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if column exists
    cur.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cur.fetchall()]
    if "password_hash" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        print("Added column password_hash")
    else:
        print("Column password_hash already exists")

    # Backfill any NULL or empty values
    default_hash = pwd_context.hash("password123")
    cur.execute(
        "UPDATE users SET password_hash = ? WHERE password_hash IS NULL OR password_hash = ''",
        (default_hash,)
    )
    conn.commit()
    print(f"Backfilled rows: {cur.rowcount}")
    conn.close()


if __name__ == "__main__":
    ensure_password_hash("tasks.db")
