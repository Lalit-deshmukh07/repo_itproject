from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
 
from app.models import Task, User

class UserRepository:
    def __init__(self, db: Session):
        self._db = db
   
    def all(self) -> list[User]:
        return self._db.execute(select(User)).scalars().all()
 
    def find(self, user_id: int) -> Optional[User]:
        return self._db.get(User, user_id)
    
    def find_by_name(self, name: str) -> Optional[User]:
        return self._db.scalars(select(User).where(User.name == name)).first()

    def add(self , name: str, password_hash: str) -> User:
        user = User(name=name, password_hash=password_hash)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user
    