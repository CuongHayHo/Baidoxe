#!/usr/bin/env python3
"""
simulate_esp32_data.py - Mô phỏng ESP32 gửi dữ liệu cảm biến tới backend
Simulates HC-SR04 ultrasonic sensors reading parking slot distances
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configuration
BACKEND_URL = "http://localhost:5000"

class ESP32Simulator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.total_sensors = 15
        self.current_distances = [random.randint(20, 200) for _ in range(self.total_sensors)]
        self.scan_history = []
        
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
    
    def get_parking_data(self, reset: bool = False) -> Dict[str, Any]:
        """
        Lấy dữ liệu bãi đỗ từ backend
        
        Args:
            reset: Có yêu cầu backend reset sensors hay không
        """
        try:
            endpoint = f"{self.backend_url}/api/parking-slots/"
            params = {'reset': 'true' if reset else 'false'}
            
            response = requests.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get parking data"
            }
    
    def simulate_sensor_scan(self, duration: int = 15) -> List[int]:
        """
        Mô phỏng quá trình quét 15 sensor HC-SR04
        Mỗi sensor mất ~1 giây, tổng cộng ~15 giây
        
        Args:
            duration: Thời gian quét (giây)
        
        Returns:
            Danh sách khoảng cách từ 15 sensor
        """
        print(f"\n🔍 Bắt đầu quét {self.total_sensors} sensor HC-SR04...")
        print(f"⏱️  Thời gian dự kiến: ~{duration} giây\n")
        
        new_distances = []
        start_time = time.time()
        
        for sensor_id in range(self.total_sensors):
            # Mô phỏng thời gian đọc sensor (0.8-1.2 giây)
            sensor_time = 0.8 + random.random() * 0.4
            time.sleep(sensor_time)
            
            # Sinh dữ liệu: khoảng cách từ 10cm (có xe) đến 200cm (chỗ trống)
            # Có 30% xác suất có xe (distance <= 15cm)
            if random.random() < 0.3:
                distance = random.randint(5, 15)  # Có xe
                occupied = "🚗"
            else:
                distance = random.randint(20, 200)  # Chỗ trống
                occupied = "⬜"
            
            new_distances.append(distance)
            
            # Hiển thị tiến trình
            progress = (sensor_id + 1) / self.total_sensors * 100
            bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
            print(f"   [{bar}] {progress:5.1f}% | Slot {sensor_id + 1:02d}: {distance:3d}cm {occupied}")
        
        elapsed = time.time() - start_time
        print(f"\n✅ Quét xong trong {elapsed:.1f}s")
        
        # Cập nhật distances
        self.current_distances = new_distances
        return new_distances
    
    def send_sensor_data(self, distances: Optional[List[int]] = None) -> bool:
        """
        Gửi dữ liệu sensor tới backend
        
        Args:
            distances: Danh sách khoảng cách từ sensors
        """
        if distances is None:
            distances = self.current_distances
        
        try:
            # Format payload theo ESP32 response format
            occupied_slots = [i for i, d in enumerate(distances) if d <= 15]
            occupied_count = len(occupied_slots)
            available_count = len(distances) - occupied_count
            
            payload = {
                "success": True,
                "soIC": 2,  # Number of shift register ICs
                "totalSensors": self.total_sensors,
                "data": [
                    {
                        "slot_id": i + 1,
                        "distance": d,
                        "occupied": d <= 15,
                        "unit": "cm"
                    }
                    for i, d in enumerate(distances)
                ],
                "summary": {
                    "total_slots": self.total_sensors,
                    "occupied": occupied_count,
                    "available": available_count,
                    "occupancy_rate": round(occupied_count / self.total_sensors * 100, 1)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"\n🚀 Gửi dữ liệu sensor tới backend...")
            print(f"   Occupied: {occupied_count}/{self.total_sensors}")
            print(f"   Available: {available_count}/{self.total_sensors}")
            
            response = requests.post(
                f"{self.backend_url}/api/parking-slots/",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Backend phản hồi (200):")
                print(f"   Message: {data.get('message', 'OK')}")
                if 'summary' in data:
                    summary = data['summary']
                    print(f"   Occupied: {summary.get('occupied', 'N/A')}/{summary.get('total_slots', 'N/A')}")
                
                self.scan_history.append({
                    'occupied': occupied_count,
                    'available': available_count,
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
    
    def reset_sensors(self) -> bool:
        """Yêu cầu backend reset sensor"""
        try:
            print(f"\n🔄 Yêu cầu reset sensors...")
            
            response = requests.post(
                f"{self.backend_url}/api/parking-slots/reset",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Reset thành công:")
                print(f"   Message: {data.get('message', 'OK')}")
                return True
            else:
                print(f"\n⚠️  Reset thất bại ({response.status_code}):")
                print(f"   {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            return False
    
    def manual_set_distances(self) -> bool:
        """Cho phép nhập khoảng cách thủ công"""
        print(f"\n✏️  Nhập khoảng cách cho {self.total_sensors} slot")
        print(f"   (Nhập số từ 5-200cm, cách nhau bằng dấu phẩy)")
        print(f"   VD: 10,50,100,20,200,15,30,...")
        
        try:
            input_str = input("👉 Nhập khoảng cách: ").strip()
            distances = [int(x.strip()) for x in input_str.split(",")]
            
            if len(distances) != self.total_sensors:
                print(f"❌ Cần nhập đúng {self.total_sensors} giá trị, bạn nhập {len(distances)}")
                return False
            
            if not all(5 <= d <= 200 for d in distances):
                print(f"❌ Khoảng cách phải từ 5-200cm")
                return False
            
            self.current_distances = distances
            print(f"✅ Cập nhật khoảng cách thành công")
            return True
            
        except ValueError:
            print(f"❌ Dữ liệu nhập không hợp lệ")
            return False
    
    def show_current_state(self):
        """Hiển thị trạng thái hiện tại"""
        occupied = [i for i, d in enumerate(self.current_distances) if d <= 15]
        available = len(self.current_distances) - len(occupied)
        
        print(f"\n📊 TRẠNG THÁI HỆ THỐNG:")
        print(f"   Tổng slot: {self.total_sensors}")
        print(f"   Đã sử dụng: {len(occupied)} ({len(occupied)/self.total_sensors*100:.1f}%)")
        print(f"   Chỗ trống: {available} ({available/self.total_sensors*100:.1f}%)")
        print(f"\n📍 Chi tiết các slot:")
        
        for i, distance in enumerate(self.current_distances, 1):
            occupied_marker = "🚗" if distance <= 15 else "⬜"
            print(f"   [{i:2d}] {occupied_marker} {distance:3d}cm", end="")
            if i % 5 == 0:
                print()
            else:
                print(" | ", end="")
        print("\n")
    
    def show_scan_history(self):
        """Hiển thị lịch sử quét"""
        if not self.scan_history:
            print(f"\n📜 Lịch sử quét: Trống")
            return
        
        print(f"\n📜 Lịch sử quét ({len(self.scan_history)} lần):")
        for i, scan in enumerate(self.scan_history, 1):
            occupancy_rate = scan['occupied'] / self.total_sensors * 100
            print(f"   [{i}] {scan['time']} - Occupied: {scan['occupied']}/{self.total_sensors} ({occupancy_rate:.1f}%)")
    
    def simulate_dynamic_changes(self) -> bool:
        """Mô phỏng sự thay đổi động (xe vào/ra)"""
        print(f"\n🎬 Bắt đầu mô phỏng sự thay đổi động...")
        print(f"   Sẽ quét sensor 5 lần, mỗi lần cách 3 giây")
        
        for iteration in range(5):
            print(f"\n⏱️  Lần quét {iteration + 1}/5:")
            self.simulate_sensor_scan(duration=3)
            self.send_sensor_data()
            if iteration < 4:
                print(f"   Chờ 3s trước lần quét tiếp theo...")
                time.sleep(3)
        
        print(f"\n✅ Hoàn thành mô phỏng động")
        return True

def print_header():
    """In header"""
    print("\n")
    print("╔" + "="*60 + "╗")
    print("║" + " "*8 + "ESP32 SENSOR DATA SIMULATOR" + " "*24 + "║")
    print("║" + " "*10 + "(HC-SR04 Ultrasonic Sensors)" + " "*23 + "║")
    print("╚" + "="*60 + "╝")

def print_menu():
    """In menu options"""
    print(f"\n{'='*62}")
    print(f"OPTIONS:")
    print(f"{'='*62}")
    print(f"1️⃣  Quét sensor (15 sensors, ~15s)")
    print(f"2️⃣  Gửi dữ liệu hiện tại tới backend")
    print(f"3️⃣  Quét + Gửi dữ liệu (bước 1+2)")
    print(f"4️⃣  Xem trạng thái hiện tại")
    print(f"5️⃣  Nhập khoảng cách thủ công")
    print(f"6️⃣  Reset sensors qua backend")
    print(f"7️⃣  Mô phỏng sự thay đổi động (5 lần)")
    print(f"8️⃣  Xem lịch sử quét")
    print(f"9️⃣  Lấy dữ liệu bãi từ backend")
    print(f"0️⃣  Thoát")
    print(f"{'='*62}")

def main():
    print_header()
    
    simulator = ESP32Simulator()
    
    print(f"✅ Backend URL: {BACKEND_URL}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 Số sensors: {simulator.total_sensors}")
    
    # Check backend health
    if not simulator.check_backend_health():
        print(f"⚠️  Cảnh báo: Backend có vẻ không chạy!")
    else:
        print(f"✅ Backend đang chạy")
    
    # Main loop
    while True:
        print_menu()
        choice = input("👉 Chọn option (0-9): ").strip()
        
        if choice == "1":
            # Quét sensor
            simulator.simulate_sensor_scan()
            simulator.show_current_state()
        
        elif choice == "2":
            # Gửi dữ liệu
            simulator.send_sensor_data()
        
        elif choice == "3":
            # Quét + Gửi
            simulator.simulate_sensor_scan()
            simulator.send_sensor_data()
            simulator.show_current_state()
        
        elif choice == "4":
            # Xem trạng thái
            simulator.show_current_state()
        
        elif choice == "5":
            # Nhập thủ công
            if simulator.manual_set_distances():
                simulator.show_current_state()
        
        elif choice == "6":
            # Reset
            simulator.reset_sensors()
        
        elif choice == "7":
            # Mô phỏng động
            simulator.simulate_dynamic_changes()
            simulator.show_scan_history()
        
        elif choice == "8":
            # Lịch sử
            simulator.show_scan_history()
        
        elif choice == "9":
            # Lấy dữ liệu từ backend
            print(f"\n📥 Lấy dữ liệu từ backend...")
            data = simulator.get_parking_data()
            if data.get('success'):
                print(f"✅ Dữ liệu từ backend:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Lỗi: {data.get('error')}")
                print(f"   {data.get('message')}")
        
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
