#!/usr/bin/env python3
"""
Test DELETE /api/cards/<id> endpoint
"""
import requests
import sqlite3
import json

def test_delete_card():
    """Test deleting card via API"""
    print("\n" + "="*60)
    print("TEST: Deleting Card via API")
    print("="*60)
    
    # Use an existing card from migration
    test_card_id = "TEST002"
    
    # Check if card exists before deletion
    conn = sqlite3.connect(r"c:\Users\tranm\Desktop\IoT Team\Baidoxe\backend\data\parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cards WHERE card_number = ?", (test_card_id,))
    before_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Cards with ID {test_card_id} before deletion: {before_count}")
    
    if before_count == 0:
        print(f"[ERROR] Card {test_card_id} doesn't exist in database")
        return False
    
    # Call DELETE API
    try:
        print(f"\nCalling DELETE /api/cards/{test_card_id}")
        response = requests.delete(
            f"http://localhost:5000/api/cards/{test_card_id}",
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("[OK] Card deleted successfully via API")
            
            # Check database
            conn = sqlite3.connect(r"c:\Users\tranm\Desktop\IoT Team\Baidoxe\backend\data\parking_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cards WHERE card_number = ?", (test_card_id,))
            after_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"Cards with ID {test_card_id} after deletion: {after_count}")
            
            if after_count < before_count:
                print(f"[OK] Card was deleted from database ({before_count} -> {after_count})")
                return True
            else:
                print(f"[ERROR] Card count didn't decrease!")
                return False
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

if __name__ == '__main__':
    print("Testing Card Deletion")
    success = test_delete_card()
    
    if success:
        print("\n[SUCCESS] Test passed!")
    else:
        print("\n[FAILURE] Test failed!")
