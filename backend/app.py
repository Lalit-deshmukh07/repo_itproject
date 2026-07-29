import os
import sqlite3
import sys
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_session import Session

from backend.auth.routes import auth
from backend.common.models import db
from backend.config.settings import DB_PATH, SESSION_PATH
from backend.middleware.security import add_security_headers

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
TEMPLATE_DIR = FRONTEND_DIR / 'templates'
STATIC_CANDIDATES = [FRONTEND_DIR / 'static', FRONTEND_DIR / 'assets']
STATIC_DIR = next((path for path in STATIC_CANDIDATES if path.exists()), FRONTEND_DIR / 'static')

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(SESSION_PATH, exist_ok=True)


def initialize_database(app_instance):
    db_file = DB_PATH / 'wearitright.db'
    db_file.parent.mkdir(parents=True, exist_ok=True)
    db_file.touch(exist_ok=True)

    with app_instance.app_context():
        db.create_all()


def _ensure_outfit_schema():
    db_file = DB_PATH / 'wearitright.db'
    db_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                occasion TEXT NOT NULL,
                outerwear_item TEXT,
                top_item TEXT,
                bottom_item TEXT,
                shoes_item TEXT,
                item_data TEXT,
                weather TEXT,
                ai_note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='outfits'")
        if not cursor.fetchone():
            return

        cursor.execute("PRAGMA table_info(outfits)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'outerwear_item' not in columns:
            cursor.execute("ALTER TABLE outfits ADD COLUMN outerwear_item TEXT")
        if 'item_data' not in columns:
            cursor.execute("ALTER TABLE outfits ADD COLUMN item_data TEXT")
        if 'ai_note' not in columns:
            cursor.execute("ALTER TABLE outfits ADD COLUMN ai_note TEXT")
        conn.commit()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH / "wearitright.db"}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    initialize_database(app)
    _ensure_outfit_schema()

    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-12345')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = str(SESSION_PATH)
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    Session(app)
    CORS(app)

    @app.before_request
    def ensure_database_ready():
        if request.path.startswith('/static/'):
            return None

        try:
            initialize_database(app)
        except Exception as exc:
            app.logger.exception('Database initialization failed before request: %s', exc)

    @app.before_request
    def normalize_loopback_host():
        if request.path.startswith('/api/') or request.path.startswith('/static/'):
            return None

        host = request.host.split(':', 1)[0]
        if host not in {'localhost', '0.0.0.0'}:
            return None

        if request.environ.get('werkzeug.test'):
            return None

        port = request.host.split(':', 1)[1] if ':' in request.host else request.environ.get('SERVER_PORT', '5001')
        canonical_host = f'127.0.0.1:{port}'
        if request.host != canonical_host:
            return redirect(request.url.replace(request.host, canonical_host, 1), code=307)

        return None

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
    initialize_database(app)
    print('✓ Database initialized successfully!')

    app.run(debug=True, host='0.0.0.0', port=5001)
