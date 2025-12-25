"""
Migration Script - Migrate card logs từ JSON file sang SQLAlchemy database

Chức năng:
- Đọc tất cả entries từ card_logs.json
- Insert vào database table card_logs
- Kiểm tra duplicates (dựa trên card_number + timestamp)
- Log chi tiết về migration
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate_logs() -> Tuple[bool, str]:
    """
    Migrate logs từ card_logs.json sang database
    
    Returns:
        (success, message)
    """
    try:
        # Import after path is set
        from app import db, create_app
        from init_db import create_sqlalchemy_models
        
        # Create app context
        app = create_app()
        app_context = app.app_context()
        app_context.push()
        
        logger.info("Flask app context created")
        
        # Get CardLogModel từ init_db
        UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
        logger.info(f"CardLogModel loaded: {CardLogModel}")
        
        # Read JSON logs
        json_log_file = Path(__file__).parent.parent / "data" / "card_logs.json"
        
        if not json_log_file.exists():
            return False, f"File not found: {json_log_file}"
        
        with open(json_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        logs = log_data.get("logs", [])
        logger.info(f"Loaded {len(logs)} logs from JSON file")
        
        if len(logs) == 0:
            return True, "No logs to migrate"
        
        # Migrate logs
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        logger.info("Starting migration...")
        
        for idx, log_entry in enumerate(logs):
            try:
                card_id = log_entry.get("card_id", "unknown")
                action = log_entry.get("action", "unknown")
                timestamp_str = log_entry.get("timestamp", datetime.utcnow().isoformat())
                details = log_entry.get("details", {})
                
                # Convert timestamp string to datetime
                try:
                    if isinstance(timestamp_str, str):
                        # Handle ISO format with timezone
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = timestamp_str
                except (ValueError, AttributeError):
                    logger.warning(f"Could not parse timestamp for log {idx}: {timestamp_str}")
                    timestamp = datetime.utcnow()
                
                # Check for duplicate using db.session.query
                existing = db.session.query(CardLogModel).filter_by(
                    card_number=card_id,
                    action=action,
                    timestamp=timestamp
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new log entry
                new_log = CardLogModel(
                    card_number=card_id,
                    action=action,
                    timestamp=timestamp,
                    notes=details.get("local_time", "")
                )
                
                db.session.add(new_log)
                migrated_count += 1
                
                # Commit every 100 entries
                if migrated_count % 100 == 0:
                    db.session.commit()
                    logger.info(f"Committed {migrated_count} logs...")
                
            except Exception as e:
                logger.error(f"Error migrating log {idx}: {e}")
                error_count += 1
                db.session.rollback()
                continue
        
        # Final commit
        db.session.commit()
        
        message = f"""
Migration completed!
- Migrated: {migrated_count}
- Skipped (duplicates): {skipped_count}
- Errors: {error_count}
- Total: {migrated_count + skipped_count + error_count}/{len(logs)}
        """
        
        logger.info(message)
        
        return True, f"Successfully migrated {migrated_count} logs (skipped {skipped_count} duplicates, {error_count} errors)"
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False, f"Migration failed: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting card_logs JSON to Database migration...")
    success, message = migrate_logs()
    
    logger.info(message)
    
    if success:
        logger.info("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Migration failed!")
        sys.exit(1)
