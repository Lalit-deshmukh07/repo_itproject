from app.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository | None = None):
        self.repo = repo or TaskRepository()

    def list_tasks(self):
        return self.repo.list_tasks()

    def get_task(self, task_id: int) -> dict | None:
        return self.repo.get_task(task_id)

    def create_task(self, title: str) -> dict:
        return self.repo.add_task(title)

    def update_task(self, task_id: int, title: str | None = None) -> dict | None:
        if title is None:
            return self.get_task(task_id)
        return self.repo.update_task(task_id, title)

    def delete_task(self, task_id: int) -> bool:
        return self.repo.remove_task(task_id)

