from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
 
class UserSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserWithTasks(UserSchema):
    tasks: list["Task"] = []
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class Task(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)