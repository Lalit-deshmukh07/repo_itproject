from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
 
from app.auth.hashing import verify_password, hash_password
from app.repositories.user_repository import UserRepository
from app.auth.tokens import create_access_token
from app.schemas import User as UserSchema
from app.controllers.task_controller import get_user_repo
from app.auth.dependencies import get_current_user
from app.models import User
 
router = APIRouter()
 
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
 
class RegisterRequest(BaseModel):
    username: str
    password: str
 
@router.post("/register", response_model=UserSchema, status_code=201)
def register(payload: RegisterRequest, repo: UserRepository = Depends(get_user_repo)):
    if repo.find_by_name(payload.username):
        raise HTTPException(status_code=409, detail="Username taken")
    user = repo.add(payload.username, hash_password(payload.password))
    return user
 
@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), repo: UserRepository = Depends(get_user_repo)):
    user = repo.find_by_name(form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, detail="Incorrect credentials")
    return TokenResponse(access_token=create_access_token(user.id))

@router.get("/me", response_model=UserSchema)
def me(user: User = Depends(get_current_user)):
    return user
            