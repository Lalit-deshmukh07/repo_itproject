from flask import Blueprint, request, jsonify

auth = Blueprint('auth', __name__)

# Temporary in-memory database
users = []

# ---------------------------
# REGISTER
# ---------------------------
@auth.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    first_name = (data.get("firstName") or "").strip()
    last_name = (data.get("lastName") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    consent = data.get("consent")

    if not first_name or not last_name:
        return jsonify({"message": "First name and last name are required."}), 400

    if not email or "@" not in email or len(email) < 5:
        return jsonify({"message": "Please enter a valid email address."}), 400

    if not password or len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long."}), 400

    if consent not in [True, 'true', 'on', 'yes', '1']:
        return jsonify({"message": "You must accept the terms and privacy policy."}), 400

    for user in users:
        if user["email"] == email:
            return jsonify({"message": "User already exists"}), 400

    users.append({
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "password": password
    })

    return jsonify({"message": "Registered successfully"}), 201


# ---------------------------
# LOGIN
# ---------------------------
@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    email = data.get("email")
    password = data.get("password")

    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify({"message": "Login successful"}), 200

    return jsonify({"message": "Invalid email or password"}), 401


# ---------------------------
# PASSWORD RESET
# ---------------------------
@auth.route('/api/auth/reset-request', methods=['POST'])
def reset_request():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    email = data.get("email")

    return jsonify({
        "message": f"Password reset link sent to {email}"
    }), 200
