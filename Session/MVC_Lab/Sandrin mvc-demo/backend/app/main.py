from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from app.controllers.task_controller import router as task_router
from app.database import get_db, engine, Base
from app.models import Task
from sqlalchemy.orm import Session

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(task_router, prefix="/tasks", tags=["tasks"])

@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/db-ping")
def db_ping(db: Session = Depends(get_db)):
    """Test database connectivity and return PostgreSQL version."""
    result = db.execute(text("SELECT version()")).scalar()
    return {"version": result}