from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    last_login_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
