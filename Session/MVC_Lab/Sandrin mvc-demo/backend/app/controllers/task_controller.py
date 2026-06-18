from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.task_service import TaskService
from app.schemas import Task, TaskCreate

router = APIRouter()

@router.get("/", response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.list_tasks()

@router.post("/", response_model=Task, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.create_task(payload.title)

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.update_task(task_id, payload.title)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")