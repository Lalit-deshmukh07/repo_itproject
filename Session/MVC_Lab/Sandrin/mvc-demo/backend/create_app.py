code = """from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = 'db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {
        'users': [{'id': i+1, 'name': n} for i, n in enumerate(['Alice','Bob','Brinda','Deval','Lalit','Grishma','Sandrin'])],
        'tasks': []
    }

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(load_db()['users'])

@app.route('/tasks', methods=['GET'])
def list_tasks():
    return jsonify(load_db()['tasks'])

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    owner_id = data.get('owner_id')
    if not title or owner_id is None:
        return jsonify({'detail': 'Missing'}), 422
    db = load_db()
    if not any(u['id'] == owner_id for u in db['users']):
        return jsonify({'detail': 'Owner not found'}), 404
    task_id = max([t['id'] for t in db['tasks']], default=0) + 1
    task = {'id': task_id, 'title': title, 'owner_id': owner_id}
    db['tasks'].append(task)
    save_db(db)
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    db = load_db()
    task = next((t for t in db['tasks'] if t['id'] == task_id), None)
    if not task:
        return jsonify({'detail': 'Not found'}), 404
    if title:
        task['title'] = title
    save_db(db)
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = load_db()
    db['tasks'] = [t for t in db['tasks'] if t['id'] != task_id]
    save_db(db)
    return '', 204

if __name__ == '__main__':
    load_db()
    app.run(debug=True, port=8000, host='0.0.0.0')
"""

with open('app/main.py', 'w') as f:
    f.write(code)
print("OK")
