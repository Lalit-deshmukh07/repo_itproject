from src.database.db import get_db

def get_all_users():
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()
    return users