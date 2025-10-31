from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Create extension instances
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """
    User model for storing user details and handling authentication logic.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Level 2 - Security Enhancement Fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_locked(self):
        """Checks if the account is currently locked."""
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f'<User {self.username}>'
