"""
Backfill `password_hash` column in a Postgres `users` table.

Usage:
  - Set env var: DATABASE_URL=postgresql://user:pass@host:5432/dbname
  - or pass as arg: --db postgresql://user:pass@host:5432/dbname

Example:
  python backfill_postgres_passwords.py --db postgresql://user:pass@localhost:5432/tasks --default-password password123

The script will:
  - verify `users` table exists
  - add `password_hash` column if missing
  - backfill NULL/empty values with a hashed `--default-password`
"""

import os
import argparse
from passlib.context import CryptContext
from sqlalchemy import create_engine, text, inspect


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", help="Database URL (overrides DATABASE_URL env var)")
    p.add_argument("--default-password", default="password123", help="Default password to hash for existing users")
    args = p.parse_args()

    db_url = args.db or os.environ.get("DATABASE_URL")
    if not db_url:
        print("No database URL provided. Set DATABASE_URL or pass --db.")
        return

    engine = create_engine(db_url)
    inspector = inspect(engine)

    if 'users' not in inspector.get_table_names():
        print("'users' table not found in the target database. Aborting.")
        return

    cols = [c['name'] for c in inspector.get_columns('users')]

    with engine.begin() as conn:
        if 'password_hash' not in cols:
            print("Adding column 'password_hash' to users table...")
            # PostgreSQL: add column
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(200)"))
        else:
            print("Column 'password_hash' already exists")

        pwd = args.default_password
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        hashed = pwd_context.hash(pwd)

        print("Backfilling NULL or empty password_hash values...")
        result = conn.execute(
            text("UPDATE users SET password_hash = :h WHERE password_hash IS NULL OR password_hash = ''"),
            {"h": hashed},
        )
        try:
            updated = result.rowcount
        except Exception:
            # Some DBAPIs may not provide rowcount; fetch count manually
            updated = None

        if updated is None:
            # run a count query to determine how many were updated
            cnt = conn.execute(text("SELECT COUNT(*) FROM users WHERE password_hash = :h"), {"h": hashed}).scalar()
            print(f"Rows now with the default hash: {cnt}")
        else:
            print(f"Rows updated: {updated}")

    print("Done.")


if __name__ == '__main__':
    main()
