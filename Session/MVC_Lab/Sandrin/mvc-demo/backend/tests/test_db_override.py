import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path so `app` imports work when pytest runs inside container
# The app package is at /app/app, so add the parent directory `/app` (one level up from tests)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.database import Base
from app.hashing import hash_password
from app import main


@pytest.fixture()
def in_memory_db(monkeypatch):
    # create an in-memory SQLite DB and bind a sessionmaker to it
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # patch the app's SessionLocal so routes use the test DB
    monkeypatch.setattr('app.database.SessionLocal', TestingSessionLocal)
    # also patch any imported references in app.main that captured SessionLocal at import time
    monkeypatch.setattr('app.main.SessionLocal', TestingSessionLocal)
    return TestingSessionLocal


def test_users_endpoint_uses_test_db(in_memory_db):
    client = main.app.test_client()
    # seed a user directly using a session
    db = in_memory_db()
    from app.models import User
    u = User(name='TestUser', password_hash=hash_password('password123'))
    db.add(u)
    db.commit()
    db.refresh(u)
    db.close()

    rv = client.get('/users')
    assert rv.status_code == 200
    data = rv.get_json()
    assert any(item['name'] == 'TestUser' for item in data)


def test_users_with_tasks_endpoint(in_memory_db):
    client = main.app.test_client()
    db = in_memory_db()
    from app.models import User, Task
    u = User(name='U1', password_hash=hash_password('password123'))
    db.add(u)
    db.commit()
    db.refresh(u)
    t = Task(title='t1', owner_id=u.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    db.close()

    rv = client.get('/users/with-tasks')
    assert rv.status_code == 200
    data = rv.get_json()
    # find our user and assert tasks included
    found = next((it for it in data if it['name'] == 'U1'), None)
    assert found is not None
    assert isinstance(found.get('tasks'), list)
    assert any(task['title'] == 't1' for task in found['tasks'])
