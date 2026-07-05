
from flask import Flask, render_template
from flask_cors import CORS
import sys
import os

# Get absolute paths to ensure consistency across machines
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(BASE_DIR, 'docs/Architecture/src')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Create Flask app with explicit template and static folders
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# Now import auth blueprint after Flask is initialized
try:
    from api.auth_routes import auth
except ImportError as e:
    print(f"Error importing auth_routes: {e}")
    # Fallback: load the module directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("auth_routes", os.path.join(src_path, 'api/auth_routes.py'))
    auth_module = importlib.util.module_from_spec(spec)
    sys.modules['auth_routes'] = auth_module
    spec.loader.exec_module(auth_module)
    auth = auth_module.auth

# ✅ Register blueprint here
app.register_blueprint(auth)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/profile-setup')
def profile_setup():
    return render_template('profile_setup.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


# ✅ CORRECT LINE
if __name__ == '__main__':
    app.run(debug=True, port=5000)