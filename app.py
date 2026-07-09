
from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_session import Session
import sys
import os

# Get absolute paths to ensure consistency across machines
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(BASE_DIR, 'docs/Architecture/src')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DB_PATH = os.path.join(BASE_DIR, 'instance')
SESSION_PATH = os.path.join(DB_PATH, 'sessions')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Create directories if they don't exist
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)
if not os.path.exists(SESSION_PATH):
    os.makedirs(SESSION_PATH)

# Import database
from database.models import db

# Create Flask app with explicit template and static folders
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DB_PATH, "wearitright.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Configure session for persistent storage
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-12345')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_PATH
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60  # 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Session
Session(app)

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


def _is_authenticated():
    """Return True if a user is logged in via session."""
    return bool(session.get('user_id'))


def _no_store(response):
    """Prevent sensitive pages from being cached by browser/proxies."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
    if not _is_authenticated():
        return redirect(url_for('login', next=request.path))
    return render_template('profile_setup.html')


@app.route('/profile')
def profile():
    if not _is_authenticated():
        return redirect(url_for('login', next=request.path))
    return render_template('profile.html')


@app.route('/recommendations')
def recommendations():
    if not _is_authenticated():
        return redirect(url_for('login', next=request.path))
    return render_template('recommendations.html')


@app.after_request
def add_security_headers(response):
    """Disable caching for authenticated HTML pages that may include personal data."""
    sensitive_paths = {'/profile', '/profile-setup', '/recommendations'}
    if request.path in sensitive_paths:
        return _no_store(response)
    return response

# ✅ CORRECT LINE
if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully!")
    
    app.run(debug=True, port=5000)