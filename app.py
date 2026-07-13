from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_session import Session
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
TEMPLATE_DIR = os.path.join(SRC_DIR, 'main', 'templates')
STATIC_DIR = os.path.join(SRC_DIR, 'main', 'static')
DB_PATH = os.path.join(BASE_DIR, 'instance')
SESSION_PATH = os.path.join(DB_PATH, 'sessions')

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(SESSION_PATH, exist_ok=True)

from src.common.models import db
from src.auth.routes import auth


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DB_PATH, "wearitright.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-12345')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = SESSION_PATH
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    Session(app)
    CORS(app)

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

    return app


def _is_authenticated():
    return bool(session.get('user_id'))


def _no_store(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('✓ Database initialized successfully!')

    app.run(debug=True, host='0.0.0.0', port=5001)

