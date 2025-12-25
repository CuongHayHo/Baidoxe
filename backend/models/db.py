"""
db.py - Database initialization
Tạo SQLAlchemy instance để dùng trong toàn bộ app
"""

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()
