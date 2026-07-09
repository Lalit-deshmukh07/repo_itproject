import sqlite3
import os


def list_tables(db_path: str):
    if not os.path.exists(db_path):
        print(f"{db_path} does not exist")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    print(f"Tables in {db_path}:")
    for r in rows:
        print(" -", r[0])
    conn.close()


if __name__ == '__main__':
    list_tables('tasks.db')
    list_tables('app/tasks.db')
    list_tables('db.json')
