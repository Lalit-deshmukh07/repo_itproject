import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, Session, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://tasks_user:tasks_pw@localhost:5432/tasks")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI dependency. ONE session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
