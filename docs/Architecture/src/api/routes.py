from flask import Blueprint, jsonify
from src.controller.user_controller import get_all_users

api = Blueprint('api', __name__)

@api.route('/api/users', methods=['GET'])
def users():
    users = get_all_users()
    return jsonify([dict(u) for u in users])