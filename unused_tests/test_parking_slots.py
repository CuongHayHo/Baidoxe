#!/usr/bin/env python3
"""
Test Parking Slots API endpoints
- GET /api/parking-slots/ - Get all parking slots
- GET /api/parking-slots/reset - Reset sensors
- GET /api/parking-slots/status - Get system status
- GET /api/parking-slots/cached - Get cached data
- GET /api/parking-slots/health - Health check
- GET /api/parking-slots/slots/<slot_id> - Get single slot
- POST /api/parking-slots/update - ESP32 sensor update
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section title"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_response(response):
    """Pretty print response"""
    print(f"Status Code: {response.status_code}")
    try:
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except:
        print(f"Response: {response.text}")
        return None

def test_get_all_parking_slots():
    """Test GET /api/parking-slots/"""
    print_section("TEST 1: Get All Parking Slots")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_all_with_reset():
    """Test GET /api/parking-slots/?reset=true"""
    print_section("TEST 2: Get Parking Slots with Reset")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/?reset=true",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_reset_sensors():
    """Test POST /api/parking-slots/reset"""
    print_section("TEST 3: Reset Sensors")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/reset",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_system_status():
    """Test GET /api/parking-slots/status"""
    print_section("TEST 4: Get System Status")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/status",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_cached_data():
    """Test GET /api/parking-slots/cached"""
    print_section("TEST 5: Get Cached Data")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/cached",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_health_check():
    """Test GET /api/parking-slots/health"""
    print_section("TEST 6: Health Check")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/health",
            timeout=5
        )
        print_response(response)
        return response.status_code in [200, 503]
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_single_slot():
    """Test GET /api/parking-slots/slots/<slot_id>"""
    print_section("TEST 7: Get Single Parking Slot (slot_id=0)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/slots/0",
            timeout=5
        )
        print_response(response)
        return response.status_code in [200, 404]
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_invalid_slot():
    """Test GET /api/parking-slots/slots/<invalid_id>"""
    print_section("TEST 8: Get Invalid Parking Slot (slot_id=999)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/slots/999",
            timeout=5
        )
        print_response(response)
        return response.status_code == 400
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_update_sensor_data():
    """Test POST /api/parking-slots/update"""
    print_section("TEST 9: Update Parking Slot (Simulate ESP32 Sensor Data)")
    
    payload = {
        "slot_id": 0,
        "occupied": True,
        "timestamp": datetime.now().isoformat() + "Z",
        "sensor_value": 150
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/update",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_update_sensor_data_empty():
    """Test POST /api/parking-slots/update with empty occupied"""
    print_section("TEST 10: Update Parking Slot (occupied=False)")
    
    payload = {
        "slot_id": 0,
        "occupied": False,
        "sensor_value": 50
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/update",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_update_missing_required_field():
    """Test POST /api/parking-slots/update with missing required field"""
    print_section("TEST 11: Update with Missing Required Field (missing 'occupied')")
    
    payload = {
        "slot_id": 0,
        "sensor_value": 150
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/update",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code == 400
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_update_invalid_slot_id():
    """Test POST /api/parking-slots/update with invalid slot_id"""
    print_section("TEST 12: Update with Invalid slot_id (slot_id=999)")
    
    payload = {
        "slot_id": 999,
        "occupied": True,
        "sensor_value": 150
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/update",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code == 400
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_update_invalid_occupied_type():
    """Test POST /api/parking-slots/update with invalid occupied type"""
    print_section("TEST 13: Update with Invalid occupied Type (string instead of bool)")
    
    payload = {
        "slot_id": 0,
        "occupied": "true",  # Should be boolean
        "sensor_value": 150
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/update",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code == 400
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_get_sensor_history():
    """Test GET /api/parking-slots/history"""
    print_section("TEST 14: Get Sensor History (24 hours)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/parking-slots/history?hours=24",
            timeout=5
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_configure_esp32():
    """Test POST /api/parking-slots/configure"""
    print_section("TEST 15: Configure ESP32")
    
    payload = {
        "sensor_threshold": 100,
        "polling_interval": 1000,
        "debug_mode": True
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/parking-slots/configure",
            json=payload,
            timeout=5
        )
        print_response(response)
        return response.status_code in [200, 501]  # 501 if not implemented
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def run_all_tests():
    """Run all parking slots tests"""
    print("\n" + "="*70)
    print("  PARKING SLOTS API TEST SUITE")
    print("="*70)
    print(f"Server: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Get All Parking Slots", test_get_all_parking_slots),
        ("Get All with Reset", test_get_all_with_reset),
        ("Reset Sensors", test_reset_sensors),
        ("Get System Status", test_get_system_status),
        ("Get Cached Data", test_get_cached_data),
        ("Health Check", test_health_check),
        ("Get Single Slot", test_get_single_slot),
        ("Get Invalid Slot", test_get_invalid_slot),
        ("Update Sensor (occupied=True)", test_update_sensor_data),
        ("Update Sensor (occupied=False)", test_update_sensor_data_empty),
        ("Update Missing Field", test_update_missing_required_field),
        ("Update Invalid slot_id", test_update_invalid_slot_id),
        ("Update Invalid occupied Type", test_update_invalid_occupied_type),
        ("Get Sensor History", test_get_sensor_history),
        ("Configure ESP32", test_configure_esp32),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"\n[EXCEPTION] {e}")
            results.append((name, "ERROR"))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Print summary
    print_section("TEST SUMMARY")
    for name, status in results:
        symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{symbol} {name}: {status}")
    
    passed = sum(1 for _, s in results if s == "PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} passed")

if __name__ == "__main__":
    run_all_tests()
