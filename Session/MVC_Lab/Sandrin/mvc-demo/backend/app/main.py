import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from passlib.context import CryptContext
import jwt
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.models import User, Task

# Create all tables
Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
CORS(app)


# ============================================================================
# Password & Token Utilities
# ============================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as exc:
        print('JWT decode error:', exc)
        return None


# ============================================================================
# Authentication Helper
# ============================================================================

def get_current_user(db: Session):
    """Extract and validate the current user from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ', 1)[1].strip()
    payload = decode_access_token(token)
    if not payload:
        return None
    try:
        user_id = int(payload.get('sub'))
    except Exception:
        return None
    return db.query(User).filter(User.id == user_id).first()


# ============================================================================
# Response Serializers
# ============================================================================

def user_response(user: User):
    return {'id': user.id, 'name': user.name}


def task_response(task: Task):
    return {
        'id': task.id,
        'title': task.title,
        'owner_id': task.owner_id,
        'created_at': task.created_at.isoformat() if task.created_at else None,
    }



# ============================================================================
# Routes: Main Pages
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(STATIC_DIR, 'docs.html')


@app.route('/admin', methods=['GET'])
def admin_page():
    return send_from_directory(STATIC_DIR, 'admin.html')


@app.route('/docs', methods=['GET'])
def docs_page():
    return send_from_directory(STATIC_DIR, 'docs.html')


@app.route('/openapi.json', methods=['GET'])
def openapi():
    return send_from_directory(STATIC_DIR, 'openapi.json')


@app.route('/db-ping', methods=['GET'])
def db_ping():
    return jsonify({'status': 'ok'})


# ============================================================================
# Routes: Users
# ============================================================================

@app.route('/users', methods=['GET'])
@app.route('/users/', methods=['GET'])
def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return jsonify([user_response(u) for u in users])
    finally:
        db.close()


@app.route('/users', methods=['POST'])
@app.route('/users/', methods=['POST'])
def create_user():
    db = SessionLocal()
    try:
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        password = (data.get('password') or '').strip()
        if not name or not password:
            return jsonify({'detail': 'Name and password are required.'}), 422

        # Check if user exists
        existing = db.query(User).filter(User.name.ilike(name)).first()
        if existing:
            return jsonify({'detail': 'User already exists'}), 409

        new_user = User(name=name, password_hash=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return jsonify(user_response(new_user)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'detail': str(e)}), 500
    finally:
        db.close()


@app.route('/users/<int:user_id>/tasks', methods=['GET'])
def list_user_tasks(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'detail': 'User not found'}), 404
        tasks = db.query(Task).filter(Task.owner_id == user_id).all()
        return jsonify([task_response(t) for t in tasks])
    finally:
        db.close()


# ============================================================================
# Routes: Authentication
# ============================================================================

@app.route('/auth/register', methods=['POST'])
def auth_register():
    db = SessionLocal()
    try:
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        password = (data.get('password') or '').strip()
        if not name or not password:
            return jsonify({'detail': 'Name and password are required.'}), 422

        existing = db.query(User).filter(User.name.ilike(name)).first()
        if existing:
            return jsonify({'detail': 'User already exists'}), 409

        new_user = User(name=name, password_hash=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return jsonify(user_response(new_user)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'detail': str(e)}), 500
    finally:
        db.close()


@app.route('/auth/login', methods=['POST'])
def auth_login():
    db = SessionLocal()
    try:
        data = request.form.to_dict() if request.form else request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        if not username or not password:
            return jsonify({'detail': 'Username and password are required.'}), 422

        user = db.query(User).filter(User.name.ilike(username)).first()
        if user is None or not verify_password(password, user.password_hash):
            return jsonify({'detail': 'Incorrect credentials'}), 401

        token = create_access_token(user.id)
        return jsonify({'access_token': token, 'token_type': 'bearer'})
    finally:
        db.close()


@app.route('/auth/me', methods=['GET'])
def auth_me():
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if user is None:
            return jsonify({'detail': 'Missing or invalid authorization header'}), 401
        return jsonify(user_response(user))
    finally:
        db.close()


# ============================================================================
# Routes: Tasks
# ============================================================================

@app.route('/tasks', methods=['GET'])
@app.route('/tasks/tasks', methods=['GET'])
def list_tasks():
    db = SessionLocal()
    try:
        current_user = get_current_user(db)
        
        if current_user:
            # Authenticated user: return only their tasks
            tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
        else:
            # Unauthenticated: return all tasks (for admin panel)
            tasks = db.query(Task).all()
        
        return jsonify([task_response(t) for t in tasks])
    finally:
        db.close()


@app.route('/tasks', methods=['POST'])
@app.route('/tasks/tasks', methods=['POST'])
def create_task():
    db = SessionLocal()
    try:
        data = request.get_json(silent=True) or {}
        current_user = get_current_user(db)
        owner_id = data.get('owner_id')
        
        if current_user:
            # React frontend: use current user
            owner_id = current_user.id
        elif not owner_id:
            # No auth and no owner_id
            return jsonify({'detail': 'Missing or invalid authorization header'}), 401
        
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({'detail': 'Task title cannot be empty'}), 422

        # Verify owner exists
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            return jsonify({'detail': 'Owner user not found'}), 404

        new_task = Task(title=title, owner_id=owner_id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return jsonify(task_response(new_task)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'detail': str(e)}), 500
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['GET'])
@app.route('/tasks/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    db = SessionLocal()
    try:
        current_user = get_current_user(db)
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if task is None:
            return jsonify({'detail': 'Task not found'}), 404
        
        # If authenticated user, check ownership
        if current_user and task.owner_id != current_user.id:
            return jsonify({'detail': 'Not authorized'}), 403
        
        return jsonify(task_response(task))
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@app.route('/tasks/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return jsonify({'detail': 'Task not found'}), 404
        
        current_user = get_current_user(db)
        if current_user and task.owner_id != current_user.id:
            return jsonify({'detail': 'Not authorized'}), 403
        
        db.delete(task)
        db.commit()
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'detail': str(e)}), 500
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['PUT'])
@app.route('/tasks/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    db = SessionLocal()
    try:
        current_user = get_current_user(db)
        if current_user is None:
            return jsonify({'detail': 'Missing or invalid authorization header'}), 401
        
        data = request.get_json(silent=True) or {}
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({'detail': 'Task title cannot be empty'}), 422

        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return jsonify({'detail': 'Task not found'}), 404
        if task.owner_id != current_user.id:
            return jsonify({'detail': 'Not authorized'}), 403

        task.title = title
        db.commit()
        db.refresh(task)
        return jsonify(task_response(task))
    except Exception as e:
        db.rollback()
        return jsonify({'detail': str(e)}), 500
    finally:
        db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True)
