from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
 
from app.models import Task
 
class TaskRepository:
    def __init__(self, db: Session):
        self._db = db
   
    def all(self) -> list[Task]:
        return self._db.execute(select(Task)).scalars().all()
 
    def find(self, task_id: int) -> Optional[Task]:
        return self._db.get(Task, task_id)
   
    def add(self, title: str, owner_id: int) -> Task:
        task = Task(title=title, owner_id=owner_id)
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task
 
    def remove(self, task_id: int) -> bool:
        task = self._db.get(Task, task_id)
        if task:
            self._db.delete(task)
            self._db.commit()
            return True
        return False
    
    def all_for_user(self, owner_id: int) -> list[Task]:
        return list(self._db.scalars(select(Task).where(Task.owner_id == owner_id)))