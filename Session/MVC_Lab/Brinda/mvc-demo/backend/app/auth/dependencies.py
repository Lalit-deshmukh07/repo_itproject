import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.tokens import ALGORITHM, SECRET
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")
    user =db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
