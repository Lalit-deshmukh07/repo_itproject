import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.database import Base
from app.hashing import hash_password
from app import main
from app.models import User

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture
def db_session(monkeypatch):
    """Create a fresh in-memory DB session for each test."""
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr('app.database.SessionLocal', TestingSessionLocal)
    monkeypatch.setattr('app.main.SessionLocal', TestingSessionLocal)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def alice(db_session):
    """Provide a seeded user named Alice for tests."""
    user = User(name='Alice', password_hash=hash_password('password123'))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def client(db_session):
    """Flask test client configured to use the in-memory test DB."""
    return main.app.test_client()
