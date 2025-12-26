#!/usr/bin/env python3
"""
Test POST /api/cards/unknown endpoint
"""
import requests
import sqlite3
import json
from datetime import datetime

def count_cards_before():
    """Count cards in database before test"""
    conn = sqlite3.connect(r"c:\Users\tranm\Desktop\IoT Team\Baidoxe\backend\data\parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cards")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def test_add_unknown_card():
    """Test adding unknown card via API"""
    print("\n" + "="*60)
    print("TEST: Adding Unknown Card via API")
    print("="*60)
    
    before_count = count_cards_before()
    print(f"Cards in DB before: {before_count}")
    
    # Call API to add unknown card
    test_card_id = "UNK0001"  # 7 characters, alphanumeric
    payload = {
        "card_id": test_card_id
    }
    
    try:
        print(f"\nCalling POST /api/cards/unknown with card_id={test_card_id}")
        response = requests.post(
            "http://localhost:5000/api/cards/unknown",
            json=payload,
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201:
            print("[OK] Unknown card added successfully via API")
            
            # Check database
            after_count = count_cards_before()
            print(f"\nCards in DB after: {after_count}")
            
            if after_count > before_count:
                print(f"[OK] Card was saved to database ({before_count} -> {after_count})")
                
                # Verify the specific card
                conn = sqlite3.connect(r"c:\Users\tranm\Desktop\IoT Team\Baidoxe\backend\data\parking_system.db")
                cursor = conn.cursor()
                cursor.execute("SELECT card_number, owner_name, card_type FROM cards WHERE card_number = ?", (test_card_id,))
                card = cursor.fetchone()
                conn.close()
                
                if card:
                    print(f"[OK] Card found in database: {card}")
                    return True
                else:
                    print(f"[ERROR] Card {test_card_id} NOT found in database")
                    return False
            else:
                print(f"[ERROR] Card count didn't increase!")
                return False
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

if __name__ == '__main__':
    print("Testing Unknown Card Addition")
    success = test_add_unknown_card()
    
    if success:
        print("\n[SUCCESS] Test passed!")
    else:
        print("\n[FAILURE] Test failed!")
