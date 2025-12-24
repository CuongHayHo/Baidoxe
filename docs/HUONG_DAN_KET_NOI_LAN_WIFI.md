# 🌐 Hướng Dẫn Kết Nối Hệ Thống qua Mạng LAN + WiFi

## 📋 Tình Huống
- **PC**: Kết nối cả WiFi UNO R4 (192.168.4.x) và dây LAN có internet (192.168.1.x hoặc tương tự)
- **Mục tiêu**: Frontend có thể access backend qua IP LAN để có internet khi đang phát triển

---

## 🔧 Bước 1: Kiểm Tra Cấu Hình Mạng Hiện Tại

### Trên PC (Windows)
Mở PowerShell và chạy:
```powershell
# Xem tất cả network interfaces
ipconfig /all

# Tìm 2 adapters:
# 1. WiFi adapter kết nối UNO R4 (Adapter: Wireless LAN adapter WiFi)
#    IPv4 Address: 192.168.4.x (DHCP hoặc static)
#
# 2. Ethernet adapter kết nối LAN (Adapter: Ethernet adapter Ethernet)
#    IPv4 Address: 192.168.1.x (hoặc IP LAN khác)
```

### Kết Quả Mong Muốn
```
Adapter 1 - WiFi (Kết nối UNO R4):
  IPv4 Address: 192.168.4.100 (ví dụ)
  
Adapter 2 - Ethernet (Kết nối LAN/Internet):
  IPv4 Address: 192.168.1.50 (ví dụ)
```

---

## ⚙️ Bước 2: Cấu Hình UNO R4 Nhận IP từ LAN

### Hiện Tại
UNO R4 chỉ là **Access Point (AP)** - phát WiFi
- IP: 192.168.4.2
- Subnet: 192.168.4.x/24

### Mô Tả Tổng Quát (Tùy Chọn - Nâng Cao)

Để UNO R4 có thể access Internet qua LAN, bạn cần:
1. **Kết nối UNO R4 qua Ethernet** (nếu có port Ethernet shield)
2. Hoặc **Sử dụng Wifi ở chế độ Station + AP đồng thời** (phức tạp)

**Đơn giản nhất: Giữ nguyên cấu hình UNO R4 là AP, chỉ sửa Backend để listen trên cả 2 interface**

---

## 🖥️ Bước 3: Cấu Hình Backend Flask

### Cách 1: Phát Hiện Tự Động (Khuyên Dùng)

Chỉnh sửa `backend/config/config.py`:

```python
def detect_api_host():
    """Phát hiện IP để backend listen - ưu tiên LAN"""
    import socket
    import os
    
    # Thứ tự ưu tiên:
    # 1. Biến môi trường (nếu được set)
    if os.environ.get('API_HOST'):
        return os.environ.get('API_HOST')
    
    # 2. IP LAN (nếu có internet)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        host = s.getsockname()[0]
        s.close()
        print(f"✅ Backend sẽ listen trên IP LAN: {host}")
        return host
    except:
        pass
    
    # 3. IP WiFi UNO R4
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.4.2", 80))
        host = s.getsockname()[0]
        s.close()
        print(f"📡 Backend sẽ listen trên IP WiFi: {host}")
        return host
    except:
        pass
    
    # 4. Fallback - listen trên tất cả interfaces
    print("⚠️ Không phát hiện được mạng, listen trên 0.0.0.0")
    return "0.0.0.0"

API_HOST = detect_api_host()
API_PORT = 5000
```

### Cách 2: Set Tĩnh (Nếu biết IP LAN)

```bash
# Windows PowerShell
$env:API_HOST = "192.168.1.50"  # IP LAN của PC (hoặc IP Backend PC khác)
python run.py
```

Hoặc chỉnh trong `config.py`:
```python
API_HOST = "192.168.1.50"  # IP LAN cụ thể
```

---

## 🎯 Bước 4: Cấu Hình Frontend Để Kết Nối

### Cách 1: Tự Động Phát Hiện (Hiện Tại)

Frontend hiện tại đã có **smart detection** trong `src/api.ts`:

```typescript
const getApiBaseUrl = () => {
  // Nếu là localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000';
  }
  
  // Nếu là IP khác (LAN), dùng cùng IP
  return `http://${window.location.hostname}:5000`;
};

// Fallback URLs để thử lần lượt
const FALLBACK_URLS = [
  'http://192.168.4.3:5000',  // IP Backend (WiFi UNO R4)
  'http://192.168.1.50:5000', // IP Backend LAN (thêm IP LAN vào đây)
  'http://127.0.0.1:5000',
  'http://localhost:5000'
];
```

### Cách 2: Set Tĩnh trong Code

Chỉnh sửa `frontend/src/api.ts` và thêm IP LAN:

```typescript
const FALLBACK_URLS = [
  'http://192.168.1.50:5000',  // IP LAN Backend - THÊM DÒNG NÀY
  'http://192.168.4.3:5000',   // IP WiFi Backend
  'http://127.0.0.1:5000',
  'http://localhost:5000'
];
```

---

## 🚀 Bước 5: Cách Chạy Hệ Thống

### Trên UNO R4 (Không thay đổi)
```
Upload code lên Arduino như bình thường
UNO R4 sẽ:
- Phát WiFi: UNO-R4-AP (192.168.4.2)
- Listen HTTP trên port 80
```

### Trên PC - Backend (LAN/WiFi)

**Cách 1: Chạy trực tiếp (Dev)**
```bash
cd backend
python run.py

# Output:
# ✅ Backend sẽ listen trên IP LAN: 192.168.1.50
# Running on http://192.168.1.50:5000
```

**Cách 2: Set biến môi trường trước**
```powershell
# Windows PowerShell
$env:API_HOST = "192.168.1.50"
python run.py
```

### Trên PC - Frontend (LAN)

**Cách 1: Development Server**
```bash
cd frontend
npm start

# Mở browser:
# - localhost:3000 - sẽ thử localhost:5000 trước, sau đó fallback
# - 192.168.1.50:3000 - sẽ dùng 192.168.1.50:5000
```

**Cách 2: Build + Serve từ Backend**
```bash
# Build React app
npm run build

# Backend sẽ serve static files từ build/
# Mở: http://192.168.1.50:5000/
```

---

## ✅ Kiểm Tra Kết Nối

### Test Backend

```powershell
# Kiểm tra Backend listen trên cổng 5000
netstat -an | findstr 5000

# Nên thấy:
# TCP  0.0.0.0:5000  LISTENING
```

### Test từ Browser

```javascript
// Mở DevTools Console và chạy:
fetch('http://192.168.1.50:5000/api/cards')
  .then(r => r.json())
  .then(data => console.log(data))
```

Nếu thành công, sẽ thấy danh sách thẻ hoặc `{"success": true, ...}`

### Test UNO R4 WiFi vẫn hoạt động

```bash
ping 192.168.4.2

# Nên nhận được response
```

---

## 🔄 Tóm Tắt Kiến Trúc Mạng

```
┌─────────────────────────────────────────────────────────┐
│                         PC (Bạn)                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │                                                   │   │
│  │  WiFi Adapter: 192.168.4.100 ━━━━━━━━━━━━━━┓  │   │
│  │                                              ┃   │   │
│  │  Ethernet Adapter: 192.168.1.50 ━━━━━━━━┓  ┃   │   │
│  │         │                           │   ┃   │   │
│  │         ▼                           ▼   ┃   │   │
│  │  ┌──────────────┐          ┌───────────┐ ┃   │   │
│  │  │ React Dev    │          │ Flask     │◄┛   │   │
│  │  │ localhost:   │◄────────►│ Backend   │    │   │
│  │  │ 3000         │          │ 5000      │    │   │
│  │  └──────────────┘          └────────┬──┘    │   │
│  │         │                          │        │   │
│  │         └──────────┬───────────────┘        │   │
│  │                    │                        │   │
│  │              Browser Access                 │   │
│  │          localhost:3000                    │   │
│  │         (nếu dev server)                   │   │
│  └──────────────────────────────────────────────┘   │
│         │                         │                  │
│         │                         │                  │
│         └─────────────┬───────────┘                  │
└─────────────────────┼──────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌──────────┐           ┌──────────────┐
    │ Internet │           │ UNO R4 WiFi  │
    │  (LAN)   │           │ AP 192.168.4.2
    └──────────┘           │ ESP32, Sensors
                           └──────────────┘
```

---

## 🆘 Troubleshooting

### 1. Frontend không connect được Backend qua LAN

**Triệu chứng:**
```
❌ Failed to fetch http://192.168.1.50:5000/api/cards
CORS error hoặc Network error
```

**Giải pháp:**
- Kiểm tra `ipconfig /all` - IP LAN có đúng không?
- Kiểm tra Firewall: `netstat -an | findstr 5000`
- Backend có listen trên 192.168.1.50 không?
- Thử ping: `ping 192.168.1.50`

### 2. WiFi UNO R4 bị mất khi kết nối LAN

**Triệu chứng:**
Chỉ có 1 adapter (LAN hoặc WiFi), không có cả 2

**Giải pháp:**
- Kiểm tra WiFi settings: không tắt WiFi khi kết nối LAN
- Priority của WiFi network có cao không?
- Test: `ipconfig /all` - phải có 2 adapters

### 3. Backend listen trên 0.0.0.0 (không xác định)

**Giải pháp:**
Set tĩnh trong `config.py`:
```python
API_HOST = "192.168.1.50"  # IP LAN cụ thể
```

---

## 📝 Cấu Hình Ví Dụ (Copy-Paste)

### Giả sử:
- IP LAN Backend PC: `192.168.1.100`
- IP WiFi UNO R4: `192.168.4.2`

### Backend Config (`config.py`)
```python
API_HOST = "192.168.1.100"  # Hoặc để auto-detect
API_PORT = 5000
```

### Frontend Config (`src/api.ts`)
```typescript
const FALLBACK_URLS = [
  'http://192.168.1.100:5000',  // IP LAN
  'http://192.168.4.3:5000',    // IP WiFi (nếu backend chạy trên UNO)
  'http://localhost:5000',
];
```

---

**✅ Xong! Bây giờ Frontend có thể access Backend qua mạng LAN khi PC kết nối dây LAN + WiFi UNO R4.**

Hãy cho tôi biết IP LAN thực tế của bạn để tôi giúp cấu hình cụ thể!
