from flask import Blueprint, jsonify, request
from pydantic import BaseModel, ValidationError

from app.auth.tokens import create_access_token, decode_access_token
from app.database import SessionLocal
from app.hashing import hash_password, verify_password
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserSchema

auth_router = Blueprint("auth", __name__, url_prefix="/auth")


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def get_current_user() -> User | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == int(user_id)).first()
    finally:
        db.close()


@auth_router.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict() if request.form else request.get_json(silent=True)
    try:
        payload = LoginRequest(**(data or {}))
    except ValidationError as exc:
        return jsonify({"detail": exc.errors()}), 422

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        user = repo.find_by_name(payload.username)
        if user is None or not verify_password(payload.password, user.password_hash):
            return jsonify({"detail": "Incorrect credentials"}), 401

        access_token = create_access_token(user.id)
        user.last_login_token = access_token
        db.commit()
        token_response = TokenResponse(access_token=access_token)
        return jsonify(token_response.model_dump()), 200
    finally:
        db.close()


@auth_router.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    try:
        payload = RegisterRequest(**(data or {}))
    except ValidationError as exc:
        return jsonify({"detail": exc.errors()}), 422

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if repo.find_by_name(payload.name) is not None:
            return jsonify({"detail": "User already exists"}), 409

        hashed_password = hash_password(payload.password)
        user = repo.add(payload.name, hashed_password)
        return jsonify(UserSchema.model_validate(user).model_dump()), 201
    finally:
        db.close()


@auth_router.route("/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"detail": "Missing or invalid authorization header"}), 401

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception:
        return jsonify({"detail": "Invalid or expired token"}), 401

    user_id = payload.get("sub")
    if user_id is None:
        return jsonify({"detail": "Invalid token payload"}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            return jsonify({"detail": "User not found"}), 404
        return jsonify(UserSchema.model_validate(user).model_dump())
    finally:
        db.close()
