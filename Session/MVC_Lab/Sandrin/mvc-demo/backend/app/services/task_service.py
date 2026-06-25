from sqlalchemy.orm import Session
from app.models import User
from app.repositories.task_repository import TaskRepository


class UserNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)

    def list_tasks(self, current_user_id: int):
        tasks = self.repo.find_by_owner(current_user_id)
        return [
            {"id": task.id, "title": task.title, "owner_id": task.owner_id}
            for task in tasks
        ]

    def get_task(self, task_id: int, current_user_id: int) -> dict:
        task = self.repo.find(task_id)
        if task is None:
            raise TaskNotFoundError()
        if task.owner_id != current_user_id:
            raise NotAuthorizedError()
        return {"id": task.id, "title": task.title, "owner_id": task.owner_id}

    def create_task(self, title: str, current_user_id: int) -> dict:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")

        owner = self.db.get(User, current_user_id)
        if owner is None:
            raise UserNotFoundError(f"User with id={current_user_id} not found")

        task = self.repo.add(title, current_user_id)
        return {"id": task.id, "title": task.title, "owner_id": task.owner_id}

    def update_task(self, task_id: int, title: str | None, current_user_id: int) -> dict:
        task = self.repo.find(task_id)
        if task is None:
            raise TaskNotFoundError()
        if task.owner_id != current_user_id:
            raise NotAuthorizedError()
        if title is not None:
            title = title.strip()
            if title:
                task.title = title
                self.db.commit()
                self.db.refresh(task)
        return {"id": task.id, "title": task.title, "owner_id": task.owner_id}

    def delete_task(self, task_id: int, current_user_id: int) -> None:
        task = self.repo.find(task_id)
        if task is None:
            raise TaskNotFoundError()
        if task.owner_id != current_user_id:
            raise NotAuthorizedError()
        self.repo.remove(task_id) 