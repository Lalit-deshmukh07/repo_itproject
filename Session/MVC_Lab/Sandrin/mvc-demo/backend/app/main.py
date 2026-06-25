import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

PORT = int(os.environ.get('PORT', '8000'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, text, inspect

from alembic import command
from alembic.config import Config

from app.controllers.auth_controller import auth_router, get_current_user

from app.database import SessionLocal, engine, Base
from app.hashing import hash_password
from app.models import User, Task
from app.schemas import UserSchema, UserWithTasks, Task as TaskSchema, TaskCreate
from app.services.task_service import TaskService, TaskNotFoundError, NotAuthorizedError, UserNotFoundError
from sqlalchemy.orm import selectinload

app = Flask(__name__)
CORS(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_db():
    """Seed default users if the database is already initialized."""
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            default_password = hash_password("password123")
            default_users = [
                User(name="Alice", password_hash=default_password),
                User(name="Bob", password_hash=default_password),
                User(name="Brinda", password_hash=default_password),
                User(name="Deval", password_hash=default_password),
                User(name="Lalit", password_hash=default_password),
                User(name="Grishma", password_hash=default_password),
                User(name="Sandrin", password_hash=default_password),
            ]
            db.add_all(default_users)
            db.commit()
    finally:
        db.close()


@app.route('/users', methods=['GET'])
def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return jsonify([UserSchema.model_validate(u).model_dump() for u in users])
    finally:
        db.close()


@app.route('/users/with-tasks', methods=['GET'])
def users_with_tasks():
    db = SessionLocal()
    try:
        # eager load tasks to avoid N+1 queries
        stmt = select(User).options(selectinload(User.tasks))
        users = db.scalars(stmt).all()
        return jsonify([UserWithTasks.model_validate(u).model_dump(mode='json') for u in users])
    finally:
        db.close()


@app.route('/tasks', methods=['GET'])
def list_tasks():
    current_user = get_current_user()
    if current_user is None:
        return jsonify({'detail': 'Missing or invalid authorization header'}), 401

    db = SessionLocal()
    try:
        service = TaskService(db)
        tasks = service.list_tasks(current_user.id)
        return jsonify(tasks)
    finally:
        db.close()


@app.route('/tasks', methods=['POST'])
def create_task():
    current_user = get_current_user()
    if current_user is None:
        return jsonify({'detail': 'Missing or invalid authorization header'}), 401

    data = request.get_json() or {}

    try:
        task_create = TaskCreate(**data)
    except (ValidationError, ValueError) as e:
        return jsonify({'detail': str(e)}), 422

    db = SessionLocal()
    try:
        service = TaskService(db)
        task = service.create_task(task_create.title, current_user.id)
        return jsonify(task), 201
    except UserNotFoundError:
        return jsonify({'detail': 'User not found'}), 404
    except ValueError as e:
        return jsonify({'detail': str(e)}), 422
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    current_user = get_current_user()
    if current_user is None:
        return jsonify({'detail': 'Missing or invalid authorization header'}), 401

    db = SessionLocal()
    try:
        service = TaskService(db)
        task = service.get_task(task_id, current_user.id)
        return jsonify(task)
    except TaskNotFoundError:
        return jsonify({'detail': 'Task not found'}), 404
    except NotAuthorizedError:
        return jsonify({'detail': 'Not authorized'}), 403
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    current_user = get_current_user()
    if current_user is None:
        return jsonify({'detail': 'Missing or invalid authorization header'}), 401

    data = request.get_json() or {}
    
    db = SessionLocal()
    try:
        service = TaskService(db)
        task = service.update_task(task_id, data.get('title'), current_user.id)
        return jsonify(task)
    except TaskNotFoundError:
        return jsonify({'detail': 'Task not found'}), 404
    except NotAuthorizedError:
        return jsonify({'detail': 'Not authorized'}), 403
    except ValueError as e:
        return jsonify({'detail': str(e)}), 422
    finally:
        db.close()


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    current_user = get_current_user()
    if current_user is None:
        return jsonify({'detail': 'Missing or invalid authorization header'}), 401

    db = SessionLocal()
    try:
        service = TaskService(db)
        service.delete_task(task_id, current_user.id)
        return '', 204
    except TaskNotFoundError:
        return jsonify({'detail': 'Task not found'}), 404
    except NotAuthorizedError:
        return jsonify({'detail': 'Not authorized'}), 403
    finally:
        db.close()


@app.route('/admin', methods=['GET'])
def admin_page():
    # Simple single-file admin UI to add/delete tasks using the existing API
    html = """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Tasks Admin</title>
        <style>
            body{font-family:Arial,Helvetica,sans-serif;margin:24px}
            input,select{padding:8px;margin-right:8px}
            button{padding:8px}
            li{margin-bottom:8px}
        </style>
    </head>
    <body>
        <h2>Tasks Admin</h2>
        <form id="addForm">
            <input id="title" placeholder="Task title" required />
            <input id="owner" placeholder="Owner id" type="number" required />
            <button>Add</button>
        </form>
        <p id="msg" style="color:crimson"></p>
        <ul id="tasks"></ul>

        <script>
            async function loadTasks(){
                const list = document.getElementById('tasks');
                list.innerHTML = 'Loading...';
                try{
                    const res = await fetch('/tasks');
                    const data = await res.json();
                    list.innerHTML = '';
                    data.forEach(t => {
                        const li = document.createElement('li');
                        li.innerHTML = `<strong>${t.title}</strong> (owner: ${t.owner_id}) ` +
                            `<button data-id="${t.id}" class="del">Delete</button>`;
                        list.appendChild(li);
                    });
                    document.querySelectorAll('.del').forEach(btn => btn.addEventListener('click', async (e)=>{
                        const id = e.target.dataset.id;
                        await fetch(`/tasks/${id}`, {method:'DELETE'});
                        loadTasks();
                    }));
                }catch(err){
                    document.getElementById('msg').textContent = String(err);
                    list.innerHTML = '';
                }
            }

            document.getElementById('addForm').addEventListener('submit', async (ev)=>{
                ev.preventDefault();
                document.getElementById('msg').textContent='';
                const title = document.getElementById('title').value.trim();
                const owner_id = Number(document.getElementById('owner').value);
                try{
                    const res = await fetch('/tasks', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title, owner_id})});
                    if(!res.ok){
                        const txt = await res.text();
                        throw new Error(txt || 'Failed to create');
                    }
                    document.getElementById('title').value='';
                    document.getElementById('owner').value='';
                    loadTasks();
                }catch(err){
                    document.getElementById('msg').textContent = err.message || String(err);
                }
            });

            loadTasks();
        </script>
    </body>
    </html>
    """
    return html, 200, {'Content-Type': 'text/html'}


@app.route('/openapi.json', methods=['GET'])
def openapi_json():
    spec = {
            "openapi": "3.0.0",
            "info": {"title": "Tasks API", "version": "1.0.0"},
            "servers": [{"url": "http://localhost:8000"}],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {"200": {"description": "A list of users"}}
                    }
                },
                "/tasks": {
                    "get": {"summary": "Get tasks","responses": {"200": {"description": "A list of tasks"}}},
                    "post": {
                        "summary": "Create task",
                        "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/TaskCreate"}}}},
                        "responses": {"201": {"description": "Created task"}, "422": {"description": "Validation error"}}
                    }
                },
                "/tasks/{task_id}": {
                    "get": {"summary": "Get task","parameters": [{"name": "task_id","in": "path","required": True,"schema": {"type": "integer"}}],"responses": {"200": {"description": "Task"}}},
                    "put": {"summary": "Update task","parameters": [{"name": "task_id","in": "path","required": True,"schema": {"type": "integer"}}],"requestBody": {"content": {"application/json": {"schema": {"type": "object","properties": {"title": {"type": "string"}}}}}},"responses": {"200": {"description": "Updated"}}},
                    "delete": {"summary": "Delete task","parameters": [{"name": "task_id","in": "path","required": True,"schema": {"type": "integer"}}],"responses": {"204": {"description": "Deleted"}}}
                },
                "/auth/register": {
                    "post": {
                        "summary": "Register",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/RegisterRequest"}
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created user"}, "409": {"description": "User already exists"}, "422": {"description": "Validation error"}}
                    }
                },
                "/auth/login": {
                    "post": {
                        "summary": "Login",
                        "requestBody": {
                            "content": {
                                "application/x-www-form-urlencoded": {
                                    "schema": {"$ref": "#/components/schemas/LoginRequest"}
                                }
                            }
                        },
                        "responses": {"200": {"description": "Token response"}, "401": {"description": "Incorrect credentials"}, "422": {"description": "Validation error"}}
                    }
                },
                "/auth/me": {
                    "get": {
                        "summary": "Me",
                        "security": [{"bearerAuth": []}],
                        "responses": {"200": {"description": "Authenticated user"}, "401": {"description": "Unauthorized"}, "404": {"description": "User not found"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {"type": "object","properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
                    "Task": {"type": "object","properties": {"id": {"type": "integer"}, "title": {"type": "string"}, "owner_id": {"type": "integer"}, "created_at": {"type": "string"}}},
                    "TaskCreate": {"type": "object","required": ["title"],"properties": {"title": {"type": "string"}}},
                    "RegisterRequest": {"type": "object","properties": {"name": {"type": "string"}, "password": {"type": "string"}}, "required": ["name", "password"]},
                    "LoginRequest": {"type": "object","properties": {"username": {"type": "string"}, "password": {"type": "string"}}, "required": ["username", "password"]},
                    "TokenResponse": {"type": "object","properties": {"access_token": {"type": "string"}, "token_type": {"type": "string"}}},
                    "User": {"type": "object","properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "last_login_token": {"type": "string"}}}
                },
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
    return jsonify(spec)


@app.route('/docs', methods=['GET'])
def swagger_ui():
    # Serve a minimal Swagger UI that points to /openapi.json
    html = """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8" />
          <title>API Docs</title>
          <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
          <style>body{margin:0;padding:0}</style>
        </head>
        <body>
          <div id="swagger-ui"></div>
          <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
          <script>
            const ui = SwaggerUIBundle({
              url: '/openapi.json',
              dom_id: '#swagger-ui',
              deepLinking: true,
              presets: [SwaggerUIBundle.presets.apis],
            });
          </script>
        </body>
        </html>
        """
    return html, 200, {'Content-Type': 'text/html'}


app.register_blueprint(auth_router)


def run_migrations() -> None:
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL', alembic_cfg.get_main_option('sqlalchemy.url')))
    command.upgrade(alembic_cfg, 'head')


def ensure_password_hash_column() -> None:
    inspector = inspect(engine)
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'password_hash' not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(200)"))
                default_hash = hash_password('password123')
                conn.execute(text("UPDATE users SET password_hash = :hash"), {'hash': default_hash})
                conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL"))
                conn.commit()


if __name__ == '__main__':
    run_migrations()
    ensure_password_hash_column()
    seed_db()
    app.run(debug=True, host='0.0.0.0', port=PORT)

