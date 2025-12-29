"""
Database initialization script for SQLAlchemy models
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config, DATABASE_PATH, DATABASE_DIR
from datetime import datetime, timedelta
import bcrypt

# Initialize Flask app and database
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Import models after db initialization
from models.user import User
from models.card import Card
from models.card_log import CardLog
from models.parking_slot import ParkingSlot
from models.parking_config import ParkingConfig


def create_sqlalchemy_models():
    """Create SQLAlchemy table models using db.Model"""
    
    class UserModel(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(120), unique=True)
        full_name = db.Column(db.String(120))
        role = db.Column(db.String(20), default='staff')  # 'admin', 'staff'
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<User {self.username}>'
    
    class CardModel(db.Model):
        __tablename__ = 'cards'
        
        id = db.Column(db.Integer, primary_key=True)
        card_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
        card_type = db.Column(db.String(20), nullable=False)  # 'resident', 'temporary', 'unknown'
        owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # NULL for 'unknown' type
        owner_name = db.Column(db.String(120))
        owner_phone = db.Column(db.String(20))
        license_plate = db.Column(db.String(20))
        vehicle_info = db.Column(db.String(255))
        status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'blacklist'
        parking_slot = db.Column(db.String(20))
        contract_end_date = db.Column(db.DateTime)  # For 'resident' type
        parking_fee = db.Column(db.Float)  # For 'temporary' type
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<Card {self.card_number}>'
    
    class CardLogModel(db.Model):
        __tablename__ = 'card_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        card_number = db.Column(db.String(50), index=True)
        action = db.Column(db.String(10))  # 'in', 'out'
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        location = db.Column(db.String(100))
        parking_slot = db.Column(db.String(20))
        duration_minutes = db.Column(db.Integer)
        calculated_fee = db.Column(db.Float)
        notes = db.Column(db.String(255))
        
        def __repr__(self):
            return f'<CardLog {self.card_number} {self.action}>'
    
    class ParkingSlotModel(db.Model):
        __tablename__ = 'parking_slots'
        
        id = db.Column(db.Integer, primary_key=True)
        slot_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
        status = db.Column(db.String(20), default='empty')  # 'empty', 'occupied', 'reserved'
        assigned_card_id = db.Column(db.String(50))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<ParkingSlot {self.slot_number}>'
    
    class ParkingConfigModel(db.Model):
        __tablename__ = 'parking_config'
        
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(100), unique=True, nullable=False, index=True)
        value = db.Column(db.String(255))
        description = db.Column(db.String(255))
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<ParkingConfig {self.key}>'
    
    class LoginHistoryModel(db.Model):
        __tablename__ = 'login_history'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
        username = db.Column(db.String(80), nullable=False, index=True)
        ip_address = db.Column(db.String(45), nullable=True)
        user_agent = db.Column(db.String(500), nullable=True)
        login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        login_status = db.Column(db.String(20), default='success', nullable=False)
        failure_reason = db.Column(db.String(255), nullable=True)
        
        def __repr__(self):
            return f'<LoginHistory {self.username} at {self.login_time}>'
    
    return UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel, LoginHistoryModel


def init_db():
    """Initialize database with tables and default data"""
    
    # Create data directory if not exists
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    with app.app_context():
        print("Creating database tables...")
        
        UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel, LoginHistoryModel = create_sqlalchemy_models()
        
        db.create_all()
        print(f"✓ Database created at: {DATABASE_PATH}")
        
        # Check if admin user exists
        admin_exists = UserModel.query.filter_by(username='admin').first()
        
        if not admin_exists:
            # Create default admin user
            admin_password = 'admin123'
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user = UserModel(
                username='admin',
                password_hash=password_hash,
                email='admin@parking.com',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            print(f"✓ Default admin user created")
            print(f"  Username: admin")
            print(f"  Password: admin123")
        
        # Create default parking config if not exists
        default_configs = [
            ('hourly_rate', '50000', 'Default hourly parking rate (in VND)'),
            ('daily_rate', '500000', 'Default daily parking rate (in VND)'),
            ('system_name', 'Parking Management System', 'System name'),
        ]
        
        for key, value, description in default_configs:
            config_exists = ParkingConfigModel.query.filter_by(key=key).first()
            if not config_exists:
                config = ParkingConfigModel(key=key, value=value, description=description)
                db.session.add(config)
        
        db.session.commit()
        print(f"✓ Default configurations created")
        
        print("\n✓ Database initialization completed successfully!")


if __name__ == '__main__':
    init_db()
