from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for storing user account information."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(50))
    top_size = db.Column(db.String(10))
    bottom_size = db.Column(db.String(10))
    style_preferences = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outfits = db.relationship('Outfit', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_style_preferences(self):
        if self.style_preferences:
            return json.loads(self.style_preferences)
        return []

    def set_style_preferences(self, styles):
        self.style_preferences = json.dumps(styles) if styles else json.dumps([])

    def get_exclusions(self):
        if self.exclusions:
            return json.loads(self.exclusions)
        return []

    def set_exclusions(self, exclusions):
        self.exclusions = json.dumps(exclusions) if exclusions else json.dumps([])

    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'gender': self.gender,
            'topSize': self.top_size,
            'bottomSize': self.bottom_size,
            'stylePreferences': self.get_style_preferences(),
            'exclusions': self.get_exclusions(),
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class Outfit(db.Model):
    """Outfit model for storing saved outfits."""
    __tablename__ = 'outfits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    occasion = db.Column(db.String(120), nullable=False)
    top_item = db.Column(db.String(255))
    bottom_item = db.Column(db.String(255))
    shoes_item = db.Column(db.String(255))
    weather = db.Column(db.String(120))
    ai_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'occasion': self.occasion,
            'items': {
                'top': self.top_item,
                'bottom': self.bottom_item,
                'shoes': self.shoes_item
            },
            'weather': self.weather,
            'aiNote': self.ai_note,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
