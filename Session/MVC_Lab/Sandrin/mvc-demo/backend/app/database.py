import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, Session, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tasks.db")

# For SQLite, set connect args to allow check_same_thread=False when used with multiple threads.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Tune pool parameters for production-like Postgres usage:
    # - pool_pre_ping: detect and refresh stale connections
    # - pool_size: number of connections to keep open in the pool
    # - max_overflow: number of connections to open above pool_size when needed
    # - pool_recycle: recycle connections older than this number of seconds
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=5,
        pool_recycle=1800,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI dependency. ONE session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
