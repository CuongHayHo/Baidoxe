"""
Migration script - Transfer data from JSON files to SQLite database
Chuyển dữ liệu từ card_logs.json sang SQLite database
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config, CARDS_FILE, DATA_DIR
import bcrypt

# Initialize Flask app and database
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Define models
class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='staff')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CardModel(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    card_type = db.Column(db.String(20), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_name = db.Column(db.String(120))
    owner_phone = db.Column(db.String(20))
    license_plate = db.Column(db.String(20))
    vehicle_info = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')
    parking_slot = db.Column(db.String(20))
    contract_end_date = db.Column(db.DateTime)
    parking_fee = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CardLogModel(db.Model):
    __tablename__ = 'card_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), index=True)
    action = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    location = db.Column(db.String(100))
    parking_slot = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer)
    calculated_fee = db.Column(db.Float)
    notes = db.Column(db.String(255))

class ParkingSlotModel(db.Model):
    __tablename__ = 'parking_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    slot_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='empty')
    assigned_card_id = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParkingConfigModel(db.Model):
    __tablename__ = 'parking_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255))
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"⚠️ Invalid JSON in: {file_path}")
        return None


def migrate_card_logs():
    """Migrate card logs from JSON to SQLite"""
    print("\n📋 Starting card logs migration...")
    
    card_logs_file = DATA_DIR / "card_logs.json"
    data = load_json_file(card_logs_file)
    
    if not data or 'logs' not in data:
        print("⚠️ No card logs to migrate")
        return 0
    
    logs = data.get('logs', [])
    migrated_count = 0
    skipped_count = 0
    
    with app.app_context():
        for log_data in logs:
            try:
                # Parse timestamp
                timestamp_str = log_data.get('timestamp', '')
                try:
                    # Handle ISO format timestamp with timezone
                    if timestamp_str.endswith('+00:00'):
                        timestamp_str = timestamp_str.replace('+00:00', '')
                    timestamp = datetime.fromisoformat(timestamp_str)
                except:
                    timestamp = datetime.utcnow()
                
                # Check if log already exists
                existing_log = CardLogModel.query.filter_by(
                    card_number=log_data.get('card_id'),
                    action=log_data.get('action'),
                    timestamp=timestamp
                ).first()
                
                if existing_log:
                    skipped_count += 1
                    continue
                
                # Create new log entry
                log = CardLogModel(
                    card_number=log_data.get('card_id', 'UNKNOWN'),
                    action=log_data.get('action', 'unknown'),
                    timestamp=timestamp,
                    location=log_data.get('details', {}).get('source'),
                    notes=f"Imported from JSON"
                )
                
                db.session.add(log)
                migrated_count += 1
                
                # Commit every 100 records to avoid memory issues
                if migrated_count % 100 == 0:
                    db.session.commit()
                    print(f"  ✓ Migrated {migrated_count} logs...")
            
            except Exception as e:
                print(f"  ⚠️ Error migrating log: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        print(f"✓ Card logs migration completed:")
        print(f"  - Migrated: {migrated_count}")
        print(f"  - Skipped (already exists): {skipped_count}")
        print(f"  - Total: {len(logs)}")
        
        return migrated_count


def migrate_cards():
    """Migrate cards from JSON to SQLite (if cards.json has data)"""
    print("\n🎫 Starting cards migration...")
    
    cards_file = CARDS_FILE
    data = load_json_file(cards_file)
    
    if not data:
        print("ℹ️ Cards.json is empty or not found, skipping cards migration")
        return 0
    
    migrated_count = 0
    
    with app.app_context():
        for card_number, card_data in data.items():
            try:
                # Check if card already exists
                existing_card = CardModel.query.filter_by(card_number=card_number).first()
                
                if existing_card:
                    continue
                
                # Create new card
                card = CardModel(
                    card_number=card_number,
                    card_type='unknown',  # Default type, can be updated later
                    owner_name=card_data.get('name', 'Unknown'),
                    owner_phone=card_data.get('phone'),
                    status='active',
                )
                
                db.session.add(card)
                migrated_count += 1
            
            except Exception as e:
                print(f"  ⚠️ Error migrating card {card_number}: {e}")
                continue
        
        db.session.commit()
        print(f"✓ Cards migration completed: {migrated_count} cards migrated")
        
        return migrated_count


def migrate_unknown_cards():
    """Migrate unknown cards from unknown_cards.json to SQLite"""
    print("\n❓ Starting unknown cards migration...")
    
    unknown_cards_file = DATA_DIR / "unknown_cards.json"
    data = load_json_file(unknown_cards_file)
    
    if not data or 'unknown_cards' not in data:
        print("ℹ️ Unknown_cards.json is empty or not found, skipping")
        return 0
    
    unknown_cards = data.get('unknown_cards', [])
    migrated_count = 0
    
    with app.app_context():
        for card_data in unknown_cards:
            try:
                card_number = card_data.get('card_id')
                
                # Check if card already exists
                existing_card = CardModel.query.filter_by(card_number=card_number).first()
                
                if existing_card:
                    continue
                
                # Create new unknown card
                card = CardModel(
                    card_number=card_number,
                    card_type='unknown',  # Type is 'unknown'
                    owner_name=card_data.get('name', 'Unknown User'),
                    license_plate=card_data.get('license_plate'),
                    status='active',
                )
                
                db.session.add(card)
                migrated_count += 1
            
            except Exception as e:
                print(f"  ⚠️ Error migrating unknown card: {e}")
                continue
        
        db.session.commit()
        print(f"✓ Unknown cards migration completed: {migrated_count} cards migrated")
        
        return migrated_count


def main():
    """Main migration function"""
    print("=" * 60)
    print("🔄 JSON to SQLite Database Migration")
    print("=" * 60)
    
    with app.app_context():
        # Verify database exists
        try:
            # Try to query a table to verify database is initialized
            UserModel.query.first()
        except Exception as e:
            print(f"❌ Database not initialized. Please run init_db.py first")
            return
        
        print("✓ Database connection verified")
        
        # Run migrations
        card_logs_count = migrate_card_logs()
        cards_count = migrate_cards()
        unknown_cards_count = migrate_unknown_cards()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary")
        print("=" * 60)
        print(f"Card Logs:    {card_logs_count} records")
        print(f"Cards:        {cards_count} records")
        print(f"Unknown Cards: {unknown_cards_count} records")
        print(f"Total:        {card_logs_count + cards_count + unknown_cards_count} records")
        print("=" * 60)
        print("✓ Migration completed successfully!")


if __name__ == '__main__':
    main()
