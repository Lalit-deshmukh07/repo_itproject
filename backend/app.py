import os
import sys

from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_session import Session

from backend.auth.routes import auth
from backend.common.models import db
from backend.config.settings import DB_PATH, SESSION_PATH
from backend.middleware.security import add_security_headers

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, 'templates')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(SESSION_PATH, exist_ok=True)


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
    def apply_security_headers(response):
        return add_security_headers(response, request.path)

    return app


def _is_authenticated():
    return bool(session.get('user_id'))


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('✓ Database initialized successfully!')

    app.run(debug=True, host='0.0.0.0', port=5001)
