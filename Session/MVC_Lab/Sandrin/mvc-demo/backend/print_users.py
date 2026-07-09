import sqlite3


def show():
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cur.fetchall()]
    print('columns:', cols)
    cur.execute("SELECT id, name, substr(password_hash,1,60) FROM users")
    for r in cur.fetchall():
        print(r)
    conn.close()


if __name__ == '__main__':
    show()
