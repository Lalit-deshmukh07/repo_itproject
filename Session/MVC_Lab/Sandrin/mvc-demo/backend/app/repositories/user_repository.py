from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, name: str) -> User | None:
        return self.db.query(User).filter(User.name == name).first()

    def add(self, name: str, password_hash: str) -> User:
        user = User(name=name, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
