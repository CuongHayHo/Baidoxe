#!/usr/bin/env python3
"""
simulate_uno_card_scan.py - Mô phỏng UNO R4 quét thẻ
Gửi request tới backend với format ĐÚNG như UNO R4

Format JSON theo UNO R4:
{
  "card_id": "<UID>",
  "direction": "<IN|OUT>",
  "timestamp": ""
}

Usage:
  python simulate_uno_card_scan.py <card_id> [direction]
  
  card_id: UID của thẻ (VD: "1A2B3C4D")
  direction: 'IN' | 'OUT' (mặc định: 'IN')

Examples:
  python simulate_uno_card_scan.py "1A2B3C4D"        # Quét thẻ vào bãi
  python simulate_uno_card_scan.py "1A2B3C4D" OUT    # Quét thẻ ra bãi
"""

import requests
import json
import sys
from datetime import datetime

# Backend API URL
BACKEND_URL = "http://localhost:5000"

def simulate_card_scan(card_id: str, direction: str = "IN"):
    """
    Mô phỏng UNO R4 gửi request quét thẻ tới backend
    
    Args:
        card_id: UID của thẻ
        direction: Hướng ('IN' hoặc 'OUT')
    """
    try:
        # Tạo payload giống như UNO R4 gửi
        # Format: {"card_id": "<UID>", "direction": "<IN|OUT>", "timestamp": ""}
        payload = {
            "card_id": card_id,
            "direction": direction,
            "timestamp": ""
        }
        
        print(f"🚀 Gửi request mô phỏng UNO R4:")
        print(f"   URL: {BACKEND_URL}/api/cards/scan")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        print()
        
        # Gửi POST request tới backend
        response = requests.post(
            f"{BACKEND_URL}/api/cards/scan",
            json=payload,
            timeout=5
        )
        
        # Parse response
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend phản hồi thành công (200):")
            print(f"   {json.dumps(data, indent=2)}")
            print()
            print(f"⏱️  Desktop app sẽ nhận thông báo trong vòng 10 giây (useActivityMonitor interval)")
            print(f"📌 Kiểm tra:")
            print(f"   - Toast notification xuất hiện ở desktop app")
            print(f"   - Direction: {direction}")
            print(f"   - Card ID: {card_id}")
            return True
        else:
            print(f"⚠️  Backend phản hồi lỗi ({response.status_code}):")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Lỗi kết nối: Backend không chạy tại {BACKEND_URL}")
        print(f"   Hãy khởi động backend: python -m backend.run")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print(__doc__)
        print("❌ Vui lòng cung cấp card_id")
        sys.exit(1)
    
    card_id = sys.argv[1]
    direction = sys.argv[2].upper() if len(sys.argv) > 2 else "IN"
    
    # Validate direction
    if direction not in ["IN", "OUT"]:
        print(f"❌ Direction không hợp lệ: {direction}")
        print(f"   Chọn từ: IN, OUT")
        sys.exit(1)
    
    print(f"=" * 60)
    print(f"🧪 UNO R4 CARD SCAN SIMULATOR")
    print(f"=" * 60)
    print(f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run simulation
    success = simulate_card_scan(card_id, direction)
    
    print(f"=" * 60)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
