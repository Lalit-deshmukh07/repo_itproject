from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: title – string, max length 200.
    # Hint: mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
