import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
 
from app.main import app
from app.database import Base, get_db
from app.controllers.auth_controller import get_current_user
from app.models import User
 
@pytest.fixture
def db_session():
  
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
 
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
 
def _seed_user(db, name: str, password_hash: str) -> User:
    user = User(name=name, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
 
@pytest.fixture
def alice(db_session):
    
    return _seed_user(db_session, name="Alice", password_hash="password123")
 
@pytest.fixture
def bob(db_session):
    
    return _seed_user(db_session, name="Bob", password_hash="password123")
 
@pytest.fixture
def client(db_session, alice):
    """TestClient logged in as Alice, using the temp DB."""
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: alice
    yield TestClient(app)
    app.dependency_overrides.clear()  