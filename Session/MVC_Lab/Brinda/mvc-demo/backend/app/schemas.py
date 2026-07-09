from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    owner_id: Optional[int] = None


class Task(TaskCreate):
    id: int

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True