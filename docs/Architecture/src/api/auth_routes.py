from flask import Blueprint, request, jsonify, session
from database.models import db, User, Outfit
from datetime import datetime, timedelta

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
        
        # Automatically log in the user after registration
        session.permanent = True
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user_name'] = f"{new_user.first_name} {new_user.last_name}"
        
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
        # Set session as permanent for 7 days
        session.permanent = True
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
                {'title': 'Casual Comfort', 'description': 'Relaxed fit jeans, soft t-shirt, white sneakers', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&auto=format&fit=crop'},
                {'title': 'Weekend Vibes', 'description': 'Hoodie, chinos, canvas sneakers', 'styles': ['casual'], 'image': 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=600&auto=format&fit=crop'},
            ],
            'formal': [
                {'title': 'Business Elegant', 'description': 'Blazer, dress pants, oxford shoes', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop'},
                {'title': 'Power Suit', 'description': 'Crisp button-up, tailored trousers, leather shoes', 'styles': ['formal'], 'image': 'https://images.unsplash.com/photo-1594938298603-c8148c4b4ae2?w=600&auto=format&fit=crop'},
            ],
            'sporty': [
                {'title': 'Athletic Look', 'description': 'Sports jacket, leggings, running shoes', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1483721310020-03333e577078?w=600&auto=format&fit=crop'},
                {'title': 'Active Wear', 'description': 'Track pants, performance shirt, trainers', 'styles': ['sporty'], 'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&auto=format&fit=crop'},
            ],
            'vintage': [
                {'title': 'Retro Chic', 'description': 'Vintage blouse, high-waisted jeans, classic pumps', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop'},
                {'title': 'Nostalgic Style', 'description': 'Vintage floral dress, cardigan, loafers', 'styles': ['vintage'], 'image': 'https://images.unsplash.com/photo-1551803091-e20673f15770?w=600&auto=format&fit=crop'},
            ],
            'streetwear': [
                {'title': 'Urban Edge', 'description': 'Oversized hoodie, cargo pants, chunky sneakers', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=600&auto=format&fit=crop'},
                {'title': 'Street Style', 'description': 'Graphic tee, distressed jeans, high-tops', 'styles': ['streetwear'], 'image': 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=600&auto=format&fit=crop'},
            ],
            'minimalist': [
                {'title': 'Simple Elegance', 'description': 'Plain white tee, black jeans, white leather sneakers', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?w=600&auto=format&fit=crop'},
                {'title': 'Understated', 'description': 'Neutral sweater, tailored pants, mules', 'styles': ['minimalist'], 'image': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop'},
            ],
            'bohemian': [
                {'title': 'Boho Dream', 'description': 'Flowy maxi dress, fringe bag, strappy sandals', 'styles': ['bohemian'], 'image': 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&auto=format&fit=crop'},
                {'title': 'Free Spirit', 'description': 'Peasant blouse, wide-leg pants, wedge sandals', 'styles': ['bohemian'], 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'},
            ],
            'preppy': [
                {'title': 'Classic Prep', 'description': 'Polo shirt, chinos, boat shoes', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?w=600&auto=format&fit=crop'},
                {'title': 'Campus Chic', 'description': 'Argyle sweater, plaid skirt, loafers', 'styles': ['preppy'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
            ],
            'edgy': [
                {'title': 'Dark Edge', 'description': 'Leather jacket, ripped jeans, combat boots', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
                {'title': 'Rock Rebel', 'description': 'Band tee, black skinny jeans, Chelsea boots', 'styles': ['edgy'], 'image': 'https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?w=600&auto=format&fit=crop'},
            ],
            'romantic': [
                {'title': 'Soft Romance', 'description': 'Floral midi dress, cardigan, ballet flats', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop'},
                {'title': 'Dreamy Look', 'description': 'Lace blouse, pleated skirt, kitten heels', 'styles': ['romantic'], 'image': 'https://images.unsplash.com/photo-1519657337289-077653f724ed?w=600&auto=format&fit=crop'},
            ],
            'classic': [
                {'title': 'Timeless Classic', 'description': 'White button-down, straight trousers, ballet flats', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'},
                {'title': 'Parisian Style', 'description': 'Striped tee, wide-leg trousers, loafers', 'styles': ['classic'], 'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop'},
            ],
            'experimental': [
                {'title': 'Bold Statement', 'description': 'Mixed prints, layered accessories, statement shoes', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&auto=format&fit=crop'},
                {'title': 'Fashion Forward', 'description': 'Avant-garde silhouette, unexpected textures, bold colours', 'styles': ['experimental'], 'image': 'https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&auto=format&fit=crop'},
            ],
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


# ---------------------------
# WEATHER-BASED OUTFIT SUGGESTIONS
# ---------------------------
@auth.route('/api/outfit/weather-suggestions', methods=['GET'])
def weather_suggestions():
    """Return outfit type suggestions based on weather + occasion + user style"""
    occasion = request.args.get('occasion', 'Casual Day Out')
    condition = request.args.get('condition', 'Clear')
    temp = int(request.args.get('temp', 18))

    is_cold = temp <= 10
    is_hot = temp >= 25
    is_rainy = any(w in condition.lower() for w in ['rain', 'drizzle', 'shower'])
    is_snowy = 'snow' in condition.lower()

    weather_tag = 'cold' if is_snowy or is_cold else ('rainy' if is_rainy else ('hot' if is_hot else 'warm'))

    suggestions_map = {
        'College': {
            'hot': ['Light t-shirt + denim shorts', 'Crop top + wide-leg trousers', 'Polo + chino shorts'],
            'warm': ['Hoodie + jeans + sneakers', 'Oversized tee + cargos', 'Sweatshirt + joggers'],
            'cold': ['Puffer jacket + thermal jeans + boots', 'Knit sweater + cords + loafers'],
            'rainy': ['Waterproof jacket + dark jeans + ankle boots', 'Raincoat + joggers + trainers'],
        },
        'Office': {
            'hot': ['Linen shirt + chinos + loafers', 'Breathable dress + sandals'],
            'warm': ['Blazer + trousers + oxfords', 'Midi dress + heels', 'Shirt + suit pants'],
            'cold': ['Wool suit + overcoat', 'Turtleneck + tailored trousers + boots'],
            'rainy': ['Trench coat + dark suit + waterproof shoes'],
        },
        'Party': {
            'hot': ['Flowy sundress + sandals', 'Linen suit + loafers'],
            'warm': ['Cocktail dress + heels', 'Blazer + slim trousers + Chelsea boots'],
            'cold': ['Party dress + faux fur coat + boots', 'Velvet suit + dress shoes'],
            'rainy': ['Sequin dress + ankle boots', 'Chic raincoat + midi dress'],
        },
        'Casual Day Out': {
            'hot': ['Tank top + shorts + sandals', 'Sundress + flip-flops'],
            'warm': ['Light sweater + casual jeans + sneakers', 'Shirt dress + white sneakers'],
            'cold': ['Parka + warm layers + snow boots', 'Puffer jacket + joggers + trainers'],
            'rainy': ['Rain jacket + waterproof pants + boots', 'Anorak + jeans + wellies'],
        }
    }

    occ_map = suggestions_map.get(occasion, suggestions_map['Casual Day Out'])
    suggestions = occ_map.get(weather_tag, occ_map.get('warm', []))

    return jsonify({
        'occasion': occasion,
        'weatherTag': weather_tag,
        'condition': condition,
        'temp': temp,
        'suggestions': suggestions
    }), 200

