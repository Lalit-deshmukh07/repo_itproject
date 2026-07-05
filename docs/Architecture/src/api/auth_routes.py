from flask import Blueprint, request, jsonify, session
from database.models import db, User, Outfit
from datetime import datetime

auth = Blueprint('auth', __name__)


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

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "Registered successfully",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


# ---------------------------
# LOGIN
# ---------------------------
@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = f"{user.first_name} {user.last_name}"
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }), 200

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


# ---------------------------
# CHECK AUTH STATUS
# ---------------------------
@auth.route('/api/auth/status', methods=['GET'])
def check_auth_status():
    """Check if user is logged in"""
    user_id = session.get('user_id')
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    
    if user_id:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": user_id,
                "email": user_email,
                "name": user_name
            }
        }), 200
    
    return jsonify({
        "authenticated": False,
        "user": None
    }), 200


# ---------------------------
# SAVE OUTFIT
# ---------------------------
@auth.route('/api/outfit/save', methods=['POST'])
def save_outfit():
    """Save an outfit for logged-in user"""
    user_id = session.get('user_id')
    
    # Check if user is logged in
    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data received"}), 400
    
    # Create new outfit
    outfit = Outfit(
        user_id=user_id,
        occasion=data.get("occasion", ""),
        top_item=data.get("items", {}).get("top"),
        bottom_item=data.get("items", {}).get("bottom"),
        shoes_item=data.get("items", {}).get("shoes"),
        weather=data.get("weather", ""),
        ai_note=data.get("aiNote", "")
    )
    
    try:
        db.session.add(outfit)
        db.session.commit()
        
        return jsonify({
            "message": "Outfit saved successfully",
            "outfit": outfit.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save outfit: {str(e)}"}), 500


# ---------------------------
# GET SAVED OUTFITS
# ---------------------------
@auth.route('/api/outfit/get-all', methods=['GET'])
def get_saved_outfits():
    """Get all saved outfits for logged-in user"""
    user_id = session.get('user_id')
    
    # Check if user is logged in
    if not user_id:
        return jsonify({"message": "User not authenticated. Please login first."}), 401
    
    outfits = Outfit.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "outfits": [outfit.to_dict() for outfit in outfits],
        "totalOutfits": len(outfits)
    }), 200


# ---------------------------
# LOGOUT
# ---------------------------
@auth.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    
    return jsonify({
        "message": "Logged out successfully"
    }), 200


# ---------------------------
# SAVE USER PREFERENCES
# ---------------------------
@auth.route('/api/user/preferences', methods=['POST'])
def save_preferences():
    """Save user preferences after profile setup"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data received"}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user.gender = data.get('gender')
        user.top_size = data.get('topSize')
        user.bottom_size = data.get('bottomSize')
        user.set_style_preferences(data.get('styles', []))
        user.set_exclusions(data.get('exclusions', []))
        
        db.session.commit()
        
        return jsonify({
            "message": "Preferences saved successfully",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to save preferences: {str(e)}"}), 500


# ---------------------------
# GET USER PREFERENCES
# ---------------------------
@auth.route('/api/user/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "preferences": {
                "gender": user.gender,
                "topSize": user.top_size,
                "bottomSize": user.bottom_size,
                "styles": user.get_style_preferences(),
                "exclusions": user.get_exclusions()
            }
        }), 200
    except Exception as e:
        return jsonify({"message": f"Failed to fetch preferences: {str(e)}"}), 500


# ---------------------------
# GET RECOMMENDATIONS BASED ON STYLE
# ---------------------------
@auth.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get outfit recommendations based on user style preferences"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        styles = user.get_style_preferences()
        
        # Generate recommendations based on styles
        recommendations = []
        
        style_recommendations = {
            'casual': [
                {'title': 'Casual Comfort', 'description': 'Relaxed fit jeans, soft t-shirt, sneakers', 'styles': ['casual']},
                {'title': 'Weekend Vibes', 'description': 'Hoodie, chinos, casual shoes', 'styles': ['casual']}
            ],
            'formal': [
                {'title': 'Business Elegant', 'description': 'Blazer, dress pants, oxford shoes', 'styles': ['formal']},
                {'title': 'Professional', 'description': 'Crisp button-up, tailored trousers, leather shoes', 'styles': ['formal']}
            ],
            'sporty': [
                {'title': 'Athletic Look', 'description': 'Sports jacket, leggings, running shoes', 'styles': ['sporty']},
                {'title': 'Active Wear', 'description': 'Track pants, performance shirt, trainers', 'styles': ['sporty']}
            ],
            'vintage': [
                {'title': 'Retro Chic', 'description': 'Vintage blouse, high-waisted jeans, classic shoes', 'styles': ['vintage']},
                {'title': 'Nostalgic Style', 'description': 'Vintage dress, cardigan, loafers', 'styles': ['vintage']}
            ],
            'streetwear': [
                {'title': 'Urban Edge', 'description': 'Oversized hoodie, cargo pants, sneakers', 'styles': ['streetwear']},
                {'title': 'Street Style', 'description': 'Graphic tee, distressed jeans, high-tops', 'styles': ['streetwear']}
            ],
            'minimalist': [
                {'title': 'Simple Elegance', 'description': 'Plain white tee, black jeans, white sneakers', 'styles': ['minimalist']},
                {'title': 'Understated', 'description': 'Neutral sweater, tailored pants, minimal accessories', 'styles': ['minimalist']}
            ]
        }
        
        for style in styles:
            if style in style_recommendations:
                recommendations.extend(style_recommendations[style])
        
        return jsonify({
            "recommendations": recommendations,
            "userStyles": styles
        }), 200
    except Exception as e:
        return jsonify({"message": f"Failed to fetch recommendations: {str(e)}"}), 500
