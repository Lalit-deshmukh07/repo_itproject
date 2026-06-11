from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def list_tasks(self):
        tasks = self.repo.all()
        return [{"id": task.id, "title": task.title} for task in tasks]

    def get_task(self, task_id: int) -> dict | None:
        task = self.repo.find(task_id)
        return {"id": task.id, "title": task.title} if task else None

    def create_task(self, title: str) -> dict:
        task = self.repo.add(title)
        return {"id": task.id, "title": task.title}

    def update_task(self, task_id: int, title: str | None = None) -> dict | None:
        if title is None:
            return self.get_task(task_id)
        task = self.repo.find(task_id)
        if task:
            task.title = title
            return {"id": task.id, "title": task.title}
        return None

    def delete_task(self, task_id: int) -> bool:
        return self.repo.remove(task_id)
        return task 