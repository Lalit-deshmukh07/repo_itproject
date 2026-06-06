from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# CORS - lets your React app on port 3000/3001 call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model
class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    completed: bool = False

# Fake database - just a list in memory
tasks_db: List[Task] = []
task_id_counter = 1

@app.get("/")
def root():
    return {"message": "MVC Lab API running"}

# GET - Load all tasks
@app.get("/tasks/", response_model=List[Task])
def get_tasks():
    return tasks_db

# POST - Add new task
@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    global task_id_counter
    task.id = task_id_counter
    task_id_counter += 1
    tasks_db.append(task)
    return task

# PUT - Edit task or toggle checkbox
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task.id = task_id
            tasks_db[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

# DELETE - Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(i)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")