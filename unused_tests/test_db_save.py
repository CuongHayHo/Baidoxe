#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script - Check if database save functions work
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app import create_app, db
from scripts.init_db import create_sqlalchemy_models
from datetime import datetime, timezone
import sqlite3

def test_save_log():
    """Test save_log_to_database function"""
    print("\n" + "="*60)
    print("TEST 1: Saving log to database")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # Get models
            UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
            
            # Create a test log
            test_log = CardLogModel(
                card_number="TEST123",
                action="entry",
                timestamp=datetime.now(timezone.utc),
                notes="Test log entry"
            )
            
            db.session.add(test_log)
            db.session.commit()
            
            print("[OK] Log saved successfully to database")
            
            # Verify it was saved
            cursor = sqlite3.connect(str(backend_dir / "data" / "parking_system.db")).cursor()
            cursor.execute("SELECT COUNT(*) FROM card_logs WHERE card_number = 'TEST123' AND action = 'entry'")
            count = cursor.fetchone()[0]
            print(f"[OK] Verified: {count} log(s) found in database for TEST123")
            
            return True
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_save_card():
    """Test save_card_to_database function"""
    print("\n" + "="*60)
    print("TEST 2: Saving card to database")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # Get models
            UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
            
            # Create a test card
            test_card = CardModel(
                card_number="TESTCARD001",
                owner_name="Test Card",
                card_type="unknown",
                status="active",
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(test_card)
            db.session.commit()
            
            print("[OK] Card saved successfully to database")
            
            # Verify it was saved
            cursor = sqlite3.connect(str(backend_dir / "data" / "parking_system.db")).cursor()
            cursor.execute("SELECT COUNT(*) FROM cards WHERE card_number = 'TESTCARD001'")
            count = cursor.fetchone()[0]
            print(f"[OK] Verified: {count} card(s) found in database for TESTCARD001")
            
            return True
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_database_stats():
    """Check database stats"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    db_path = backend_dir / "data" / "parking_system.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cards")
    card_count = cursor.fetchone()[0]
    print(f"Total cards: {card_count}")
    
    cursor.execute("SELECT COUNT(*) FROM card_logs")
    log_count = cursor.fetchone()[0]
    print(f"Total logs: {log_count}")
    
    # Show last 3 logs
    cursor.execute("SELECT card_number, action, timestamp FROM card_logs ORDER BY id DESC LIMIT 3")
    logs = cursor.fetchall()
    if logs:
        print("\nLast 3 logs:")
        for log in logs:
            print(f"  - {log[0]}: {log[1]} at {log[2]}")
    
    conn.close()

if __name__ == '__main__':
    print("Testing Database Save Functions")
    print("=" * 60)
    
    check_database_stats()
    
    test_save_log()
    test_save_card()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)
    
    check_database_stats()
