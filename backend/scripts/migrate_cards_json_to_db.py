#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script: cards.json → database cards table
Migrates all cards from JSON file to database, handling duplicates
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app, db
from scripts.init_db import create_sqlalchemy_models

def migrate_cards_json_to_db():
    """Migrate cards from cards.json to database"""
    
    # Create app context
    app = create_app()
    app_context = app.app_context()
    app_context.push()
    
    # Get CardModel from SQLAlchemy
    UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
    
    # Path to cards.json
    cards_json_path = backend_dir / 'data' / 'cards.json'
    
    if not cards_json_path.exists():
        print(f"❌ File not found: {cards_json_path}")
        return
    
    # Load cards from JSON
    try:
        with open(cards_json_path, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {cards_json_path}: {e}")
        return
    
    # Handle both dict and list formats
    if isinstance(cards_data, dict):
        # cards.json format: {card_id: card_data, ...}
        print(f"📋 Found {len(cards_data)} cards in cards.json (dict format)")
        cards_list = list(cards_data.values())
    elif isinstance(cards_data, list):
        # List format
        print(f"📋 Found {len(cards_data)} cards in cards.json (list format)")
        cards_list = cards_data
    else:
        print(f"❌ Invalid format: cards.json should contain a dict or list")
        return
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for card_data in cards_list:
        try:
            card_id = card_data.get('uid') or card_data.get('id')
            
            if not card_id:
                print(f"⚠️  Skipping card without ID: {card_data}")
                skipped_count += 1
                continue
            
            # Check if card already exists in database
            existing_card = db.session.query(CardModel).filter_by(card_number=card_id).first()
            
            if existing_card:
                print(f"⏭️  Card {card_id} already exists in database, skipping")
                skipped_count += 1
                continue
            
            # Create new card record with SQLAlchemy CardModel fields
            # Mapping fields from cards.json to database schema
            new_card = CardModel(
                card_number=card_id,
                card_type='unknown',  # Default type since cards.json doesn't have card_type
                owner_name=card_data.get('name', f'Card {card_id}'),
                status='active',  # Default status
                created_at=datetime.fromisoformat(card_data.get('created_at', datetime.utcnow().isoformat())),
            )
            
            db.session.add(new_card)
            db.session.commit()
            
            print(f"✅ Migrated card: {card_id} ({card_data.get('name', 'Unknown')})")
            migrated_count += 1
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error migrating card {card_data.get('uid', 'unknown')}: {e}")
            error_count += 1
    
    print("\n" + "="*50)
    print("Migration Summary:")
    print(f"  ✅ Migrated:  {migrated_count}")
    print(f"  ⏭️  Skipped:   {skipped_count}")
    print(f"  ❌ Errors:    {error_count}")
    print("="*50)

if __name__ == '__main__':
    print("🚀 Starting cards.json → database migration...")
    print(f"⏱️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    migrate_cards_json_to_db()
    
    print(f"✨ Migration complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
