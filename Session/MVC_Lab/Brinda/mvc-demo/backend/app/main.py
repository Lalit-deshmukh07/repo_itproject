from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.task_controller import router as task_router
from app.controllers.user_controller import router as user_router
from sqlalchemy import create_engine, text
import os
from sqlalchemy import select
from app.database import SessionLocal
from app.models import User
from app.database import Base, engine
from app import models
from app.auth.hashing import hash_password 
from app.controllers.auth_controller import router as auth_router

app = FastAPI(title="MVC Task API")
 
Base.metadata.create_all(bind=engine)


def seed_users():
 """Insert two users if the table is empty."""
 with SessionLocal() as db: 
    if db.scalars(select(User)).first() is not None:
      return 
    db.add_all([
        User(username="alice", password_hash=hash_password("password123")),
        User(username="bob", password_hash=hash_password("password456")),
    ])
    db.commit()
seed_users() # call at module load


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(task_router, prefix="/tasks", tags=["tasks"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])