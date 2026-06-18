from sqlalchemy.orm import Session
from app.models import Task

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self) -> list[Task]:
        return self.db.query(Task).all()

    def find(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def add(self, title: str, owner_id: int) -> Task:
        task = Task(title=title, owner_id=owner_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def find_by_owner(self, owner_id: int) -> list[Task]:
        return self.db.query(Task).filter(Task.owner_id == owner_id).all()

    def remove(self, task_id: int) -> bool:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True

