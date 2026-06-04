from fastapi import APIRouter, HTTPException
from app.schemas import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()
service = TaskService()

@router.get("/", response_model=list[Task])
def get_tasks():
    return service.list_tasks()

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=Task, status_code=201)
def create_task(payload: TaskCreate):
    return service.create_task(payload.title)

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    task = service.update_task(task_id, payload.title)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")