#!/usr/bin/env python3
"""
interactive_card_test.py - Tool test quét thẻ interactive
Nhập UID thẻ và xem phản ứng của web (localhost:5000) real-time
"""

import requests
import json
from datetime import datetime
from typing import Optional

# Configuration
BACKEND_URL = "http://localhost:5000"

class CardTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.last_log_count = 0
        self.scanned_cards = []
    
    def check_backend_health(self) -> bool:
        """Kiểm tra backend có chạy không"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/system/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def get_current_logs_count(self) -> Optional[int]:
        """Lấy tổng số logs hiện tại"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/logs/?limit=1",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
        except:
            pass
        return None
    
    def get_latest_logs(self, limit: int = 3):
        """Lấy logs mới nhất"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/logs/?limit={limit}",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('logs', [])
        except:
            pass
        return []
    
    def scan_card(self, card_id: str, action: str = "scan", status: int = 0):
        """
        Quét thẻ - gửi request tới backend
        
        Args:
            card_id: UID của thẻ
            action: 'scan' | 'entry' | 'exit'
            status: 0 (ngoài bãi) | 1 (trong bãi)
        """
        try:
            # Format payload theo UNO R4: {card_id, direction, timestamp}
            direction = "IN" if action == "entry" else ("OUT" if action == "exit" else "IN")
            payload = {
                "card_id": card_id,
                "direction": direction,
                "timestamp": ""
            }
            
            print(f"\n🚀 Gửi request...")
            print(f"   Payload: {json.dumps(payload)}")
            
            response = requests.post(
                f"{self.backend_url}/api/cards/scan",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Backend phản hồi (200):")
                print(f"   Message: {data.get('message', 'OK')}")
                if 'status' in data:
                    print(f"   Status: {data.get('status')}")
                if 'card' in data:
                    print(f"   Card: {json.dumps(data['card'], indent=6)}")
                
                # Lưu card đã quét
                self.scanned_cards.append({
                    'uid': card_id,
                    'action': action,
                    'status': status,
                    'time': datetime.now().strftime('%H:%M:%S')
                })
                
                return True
            else:
                print(f"\n⚠️  Backend phản hồi lỗi ({response.status_code}):")
                print(f"   {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Lỗi kết nối: Backend không chạy tại {self.backend_url}")
            return False
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            return False
    
    def check_new_logs(self):
        """Kiểm tra logs mới sau khi quét"""
        print(f"\n📋 Kiểm tra logs mới (3 log mới nhất):")
        logs = self.get_latest_logs(3)
        
        if logs:
            print(f"   Found {len(logs)} log(s):")
            for i, log in enumerate(logs, 1):
                action_emoji = {
                    'scan': '📱',
                    'entry': '📥',
                    'exit': '📤',
                    'unknown': '❓'
                }.get(log.get('action', 'unknown'), '📝')
                
                print(f"\n   [{i}] {action_emoji} {log.get('action', 'unknown').upper()}")
                print(f"       Card: {log.get('card_id')}")
                print(f"       Time: {log.get('timestamp', 'N/A')}")
                if 'status' in log:
                    status_text = "Trong bãi" if log['status'] == 1 else "Ngoài bãi"
                    print(f"       Status: {status_text}")
        else:
            print(f"   Chưa có log mới")
    
    def show_history(self):
        """Hiển thị lịch sử quét"""
        if not self.scanned_cards:
            print(f"\n📜 Lịch sử quét: Trống")
            return
        
        print(f"\n📜 Lịch sử quét ({len(self.scanned_cards)} thẻ):")
        for i, card in enumerate(self.scanned_cards, 1):
            action_emoji = {
                'scan': '📱',
                'entry': '📥',
                'exit': '📤'
            }.get(card['action'], '📝')
            
            status_text = "Trong bãi" if card['status'] == 1 else "Ngoài bãi"
            print(f"   [{i}] {action_emoji} {card['uid']} - {card['action']} ({status_text}) @ {card['time']}")

def print_header():
    """In header"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*8 + "INTERACTIVE CARD SCANNER TEST TOOL" + " "*15 + "║")
    print("╚" + "="*58 + "╝")

def print_menu():
    """In menu options"""
    print(f"\n{'='*60}")
    print(f"OPTIONS:")
    print(f"{'='*60}")
    print(f"1️⃣  Quét thẻ (scan)")
    print(f"2️⃣  Xe vào bãi (entry)")
    print(f"3️⃣  Xe ra khỏi bãi (exit)")
    print(f"4️⃣  Kiểm tra logs mới")
    print(f"5️⃣  Xem lịch sử quét")
    print(f"0️⃣  Thoát")
    print(f"{'='*60}")

def main():
    print_header()
    
    tester = CardTester()
    
    print(f"✅ Backend URL: {BACKEND_URL}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main loop
    while True:
        print_menu()
        choice = input("👉 Chọn option (0-5): ").strip()
        
        if choice == "1":
            # Scan
            uid = input("📱 Nhập UID thẻ: ").strip()
            if uid:
                tester.scan_card(uid, action="scan", status=0)
                tester.check_new_logs()
        
        elif choice == "2":
            # Entry
            uid = input("📥 Nhập UID thẻ: ").strip()
            if uid:
                tester.scan_card(uid, action="entry", status=1)
                tester.check_new_logs()
        
        elif choice == "3":
            # Exit
            uid = input("📤 Nhập UID thẻ: ").strip()
            if uid:
                tester.scan_card(uid, action="exit", status=0)
                tester.check_new_logs()
        
        elif choice == "4":
            # Check logs
            tester.check_new_logs()
        
        elif choice == "5":
            # History
            tester.show_history()
        
        elif choice == "0":
            print(f"\n👋 Tạm biệt!")
            break
        
        else:
            print(f"❌ Option không hợp lệ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Dừng bởi người dùng")
