from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = None  # Will be initialized in app.py

class User:
    """User model for admin and staff roles"""
    
    def __init__(self, username, password_hash, email=None, full_name=None, role='staff'):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.full_name = full_name
        self.role = role  # 'admin' or 'staff'
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'
