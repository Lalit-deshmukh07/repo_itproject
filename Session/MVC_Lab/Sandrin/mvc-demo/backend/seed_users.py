#!/usr/bin/env python
"""Seed default users into PostgreSQL database."""

from app.database import SessionLocal, engine, Base
from app.models import User
from app.hashing import hash_password

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# User data: name and plaintext password to be hashed
users_data = [
    ("Alice", "password123"),
    ("Bob", "password123"),
    ("Brinda", "password123"),
    ("Deval", "password123"),
    ("Lalit", "password123"),
    ("Grishma", "password123"),
    ("Sandrin", "password123"),
]

db = SessionLocal()
try:
    # Check if users already exist
    existing_count = db.query(User).count()
    if existing_count > 0:
        print(f"Database already has {existing_count} users. Skipping seed.")
        exit(0)

    # Create and insert users
    for name, password in users_data:
        user = User(name=name, password_hash=hash_password(password))
        db.add(user)
        print(f"Created user: {name}")

    db.commit()
    print(f"\nSuccessfully seeded {len(users_data)} users!")
    
    # Verify
    final_count = db.query(User).count()
    print(f"Database now has {final_count} users.")
    
finally:
    db.close()
