from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    owner_id: Optional[int] = None


class Task(TaskCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)