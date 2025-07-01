import random
import string
from datetime import datetime

import bcrypt
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_superuser = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with pastes
    pastes = db.relationship(
        "Paste", backref="author", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), salt
        ).decode("utf-8")

    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat(),
            "paste_count": self.pastes.count(),
        }

    def __repr__(self):
        return f"<User {self.username}>"


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(
        db.String(16), unique=True, nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default="text")
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    views = db.Column(db.Integer, default=0)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __init__(self, **kwargs):
        super(Paste, self).__init__(**kwargs)
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()

    @staticmethod
    def generate_unique_id(length=8):
        """Generate a unique ID for the paste"""
        characters = string.ascii_letters + string.digits
        while True:
            unique_id = "".join(
                random.choice(characters) for _ in range(length)
            )
            if not Paste.query.filter_by(unique_id=unique_id).first():
                return unique_id

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.unique_id,
            "unique_id": self.unique_id,
            "title": self.title,
            "content": self.content,
            "language": self.language,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "views": self.views,
            "author": self.author.username if self.author else "Anonymous",
        }

    def __repr__(self):
        return f"<Paste {self.unique_id}: {self.title}>"
