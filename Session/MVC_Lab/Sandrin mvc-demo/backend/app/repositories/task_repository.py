from sqlalchemy.orm import Session
from app.models import Task

# from sqlalchemy.orm import Session
# from app.models import Task
#
#
# class TaskRepository:
#     def __init__(self, db: Session):
#         self.db = db
#
#     def list_tasks(self):
#         tasks = self.db.query(Task).all()
#         return [{"id": task.id, "title": task.title} for task in tasks]
#
#     def get_task(self, task_id: int):
#         task = self.db.query(Task).filter(Task.id == task_id).first()
#         return {"id": task.id, "title": task.title} if task else None
#
#     def add_task(self, title: str):
#         task = Task(title=title)
#         self.db.add(task)
#         self.db.commit()
#         self.db.refresh(task)
#         return {"id": task.id, "title": task.title}
#
#     def update_task(self, task_id: int, title: str):
#         task = self.db.query(Task).filter(Task.id == task_id).first()
#         if task is None:
#             return None
#         task.title = title
#         self.db.commit()
#         self.db.refresh(task)
#         return {"id": task.id, "title": task.title}
#
#     def remove_task(self, task_id: int):
#         task = self.db.query(Task).filter(Task.id == task_id).first()
#         if task is None:
#             return False
#         self.db.delete(task)
#         self.db.commit()
#         return True


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        return list(self.db.query(Task))

    def find(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def add(self, title: str) -> Task:
        task = Task(title=title)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def remove(self, task_id: int) -> bool:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False

