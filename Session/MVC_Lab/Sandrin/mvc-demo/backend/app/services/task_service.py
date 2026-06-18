from sqlalchemy.orm import Session
from app.models import User
from app.repositories.task_repository import TaskRepository


class UserNotFoundError(Exception):
    pass


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)

    def list_tasks(self):
        tasks = self.repo.all()
        return [
            {"id": task.id, "title": task.title, "owner_id": task.owner_id}
            for task in tasks
        ]

    def get_task(self, task_id: int) -> dict | None:
        task = self.repo.find(task_id)
        return (
            {"id": task.id, "title": task.title, "owner_id": task.owner_id}
            if task
            else None
        )

    def create_task(self, title: str, owner_id: int) -> dict:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")

        owner = self.db.get(User, owner_id)
        if owner is None:
            raise UserNotFoundError(f"User with id={owner_id} not found")

        task = self.repo.add(title, owner_id)
        return {"id": task.id, "title": task.title, "owner_id": task.owner_id}

    def update_task(self, task_id: int, title: str | None = None) -> dict | None:
        task = self.repo.find(task_id)
        if not task:
            return None
        if title is not None:
            task.title = title.strip()
            self.db.commit()
            self.db.refresh(task)
        return {"id": task.id, "title": task.title, "owner_id": task.owner_id}

    def delete_task(self, task_id: int) -> bool:
        return self.repo.remove(task_id) 