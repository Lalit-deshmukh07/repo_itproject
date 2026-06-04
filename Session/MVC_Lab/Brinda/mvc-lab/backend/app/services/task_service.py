from sqlalchemy.orm import Session
from ..models import Task
from ..schemas import TaskUpdate

class TaskService:
    def update_task(self, task_id: int, task_data: TaskUpdate, db: Session):
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        db.commit()
        db.refresh(task)
        return task