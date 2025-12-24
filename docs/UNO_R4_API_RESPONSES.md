# 🌐 UNO R4 WiFi - API Responses

## 📋 Tổng Quan

UNO R4 WiFi hoạt động như một **HTTP Server** trên port **80**:
- IP: `192.168.4.2`
- Port: `80`
- AP SSID: `UNO-R4-AP`
- WiFi Password: `12345678`

---

## 📡 Kiến Trúc Giao Tiếp

```
┌─────────────────────────────────────────────┐
│           Kiến Trúc Hai Chiều               │
├─────────────────────────────────────────────┤
│                                             │
│  UNO R4 HTTP Server (Port 80)              │
│  └─ Nhận request từ PC/Client               │
│     └─ Trả về JSON response                 │
│                                             │
│  UNO R4 HTTP Client                        │
│  └─ Gửi POST request đến Flask (5000)      │
│     └─ Nhận response từ Flask               │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔄 API Endpoints UNO R4 HTTP Server (Port 80)

### 1️⃣ **Health Check / Status Endpoint**

**Request:**
```http
GET / HTTP/1.1
Host: 192.168.4.2
Connection: close
```

**Response (HTTP 200):**
```json
{
  "status": "ok",
  "device": "UNO R4 WiFi",
  "ip": "192.168.4.2"
}
```

**Mô Tả:**
- Endpoint đơn giản để kiểm tra UNO R4 còn sống hay không
- Bất kỳ HTTP request nào cũng trả về response này
- **Không có routing** - tất cả request đều trả về cùng response

---

## 💾 Code UNO R4 Trả Response

```cpp
// Web server: Xử lý HTTP requests đơn giản
WiFiClient client = webServer.available();
if (client) {
  String request = "";
  // Đọc HTTP request từ client
  while (client.connected() && client.available()) {
    char c = client.read();
    request += c;
    if (request.endsWith("\r\n\r\n")) break; // End of HTTP header
  }
  
  // ✅ Trả về JSON response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println("{\"status\":\"ok\",\"device\":\"UNO R4 WiFi\",\"ip\":\"192.168.4.2\"}");
  client.stop();
}
```

---

## 🔑 Chi Tiết Response

| Field | Giá Trị | Mô Tả |
|-------|--------|-------|
| `status` | `"ok"` | Trạng thái hoạt động của UNO R4 |
| `device` | `"UNO R4 WiFi"` | Loại thiết bị |
| `ip` | `"192.168.4.2"` | IP tĩnh của UNO R4 (Fixed) |

---

## 📤 UNO R4 Gửi Request Đến Flask Server

UNO R4 **cũng là HTTP Client** - Khi quét thẻ RFID, nó gửi POST request đến Flask:

### **POST Request từ UNO → Flask**

**Endpoint:**
```
POST http://192.168.4.3:5000/api/cards/scan
```

**Request Body (JSON):**
```json
{
  "card_id": "A1B2C3D4",
  "direction": "IN",
  "timestamp": ""
}
```

**Code UNO R4 gửi request:**

```cpp
void sendRFIDToServer(const String& uid, const String& direction) {
  WiFiClient client;
  
  if (client.connect(serverIP.c_str(), serverPort)) {
    // Tạo JSON body
    String jsonBody = "{\"card_id\":\"" + uid + "\",\"direction\":\"" + direction + "\",\"timestamp\":\"\"}";
    
    // Tạo HTTP POST request
    String httpRequest = "POST /api/cards/scan HTTP/1.1\r\n";
    httpRequest += "Host: " + serverIP + "\r\n";
    httpRequest += "Content-Type: application/json\r\n";
    httpRequest += "Content-Length: " + String(jsonBody.length()) + "\r\n";
    httpRequest += "Connection: close\r\n\r\n";
    httpRequest += jsonBody;
    
    client.print(httpRequest);
    
    // Đọc response từ Flask
    String response = "";
    unsigned long timeout = millis() + 1000; // 1s timeout
    
    while (client.connected() && millis() < timeout) {
      if (client.available()) {
        response += client.readString();
        break;
      }
      delay(10);
    }
    client.stop();
    
    // Parse Flask response...
  }
}
```

---

## 📥 Flask Response (Nhận từ UNO)

### **Thẻ Hợp Lệ - Cho Phép Vào**

```json
{
  "success": true,
  "card": {
    "uid": "A1B2C3D4",
    "status": 1,
    "entry_time": "2025-10-21T10:30:00+00:00",
    "parking_duration": {
      "total_seconds": 0,
      "hours": 0,
      "minutes": 0,
      "display": "0 phút"
    }
  },
  "action": "entry",
  "direction": "IN",
  "message": "Card entry processed",
  "parking_status": "parked",
  "timestamp": ""
}
```

### **Thẻ Hợp Lệ - Từ Chối (Đã Ở Trong Bãi)**

```json
{
  "success": false,
  "error": "Invalid entry",
  "message": "Xe đã ở trong bãi rồi",
  "action": "reject",
  "current_status": "parked"
}
```

### **Thẻ Chưa Biết**

```json
{
  "success": false,
  "error": "Unknown card",
  "message": "Card not registered in system",
  "action": "reject",
  "card_id": "UNKNOWN123",
  "unknown_card_logged": true,
  "timestamp": ""
}
```

---

## 🔄 Quy Trình Giao Tiếp Hoàn Chỉnh

### **Sơ Đồ Timeline**

```
┌─────────────────────────────────────────────────────────────┐
│                  Timeline Quét Thẻ                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Arduino UNO R4           ←→            Flask Backend       │
│  (192.168.4.2:80)                      (192.168.4.3:5000)  │
│                                                             │
│  T=0ms: Quét thẻ                                          │
│  ├─ readRFID() phát hiện thẻ                              │
│  ├─ UID: "A1B2C3D4"                                       │
│  └─ Direction: "IN"                                        │
│      │                                                     │
│      ├─ Serial: "📡 UID IN: A1B2C3D4"                     │
│      │                                                     │
│  T=5ms: Gửi request                                       │
│  ├─ POST /api/cards/scan                                  │
│  ├─ Body: {"card_id":"A1B2C3D4","direction":"IN"...}     │
│  └─────────────────────────────────────────→              │
│                                                            │
│  T=10ms: Server xử lý (Flask)                             │
│         ├─ Kiểm tra card trong database                   │
│         ├─ Logic: IN reader + status=0 → OK               │
│         ├─ Update status = 1                              │
│         ├─ Ghi log: entry                                 │
│         └─ Tạo JSON response                              │
│                                                            │
│  T=15ms: Response trả về                                  │
│         ←──────────────────────────────                   │
│         {                                                 │
│           "success": true,                                │
│           "action": "entry",                              │
│           ...                                             │
│         }                                                 │
│                                                           │
│  T=20ms: Arduino xử lý response                           │
│  ├─ Parse JSON                                           │
│  ├─ Kiểm tra: success == true?                          │
│  ├─ Kiểm tra: action == "entry"?                        │
│  └─ YES → openBarrier(barrierIn)                        │
│                                                          │
│  T=25ms: Mở barrier                                     │
│  ├─ servo.write(90°)                                   │
│  ├─ Serial: "🚪📂 Mở barrier IN"                        │
│  └─ Xe đi qua barrier                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Test UNO R4 API Endpoints

### **Cách 1: Từ PowerShell**

```powershell
# Test health check endpoint
$response = Invoke-RestMethod -Uri "http://192.168.4.2/" -Method GET

# Xem kết quả
$response | ConvertTo-Json
```

**Output:**
```
status  : ok
device  : UNO R4 WiFi
ip      : 192.168.4.2
```

### **Cách 2: Từ Browser**

```
http://192.168.4.2/
```

**Kết quả:** Hiển thị JSON tương tự

### **Cách 3: Từ cURL (Terminal)**

```bash
# Windows PowerShell
curl -Uri "http://192.168.4.2/" -Method GET

# Output:
# {"status":"ok","device":"UNO R4 WiFi","ip":"192.168.4.2"}
```

### **Cách 4: Từ Python**

```python
import requests
import json

url = "http://192.168.4.2/"

try:
    response = requests.get(url, timeout=5)
    data = response.json()
    
    print("✅ UNO R4 Response:")
    print(json.dumps(data, indent=2))
    
except requests.exceptions.ConnectionError:
    print("❌ Không kết nối được UNO R4")
    print("   - Kiểm tra WiFi có kết nối UNO-R4-AP?")
    print("   - Kiểm tra IP 192.168.4.2 có thể ping được?")
except Exception as e:
    print(f"❌ Lỗi: {e}")
```

---

## 📊 Response Format Tóm Tắt

| Endpoint | Method | Response | Mô Tả |
|----------|--------|----------|--------|
| `/` | GET | `{"status":"ok","device":"UNO R4 WiFi","ip":"192.168.4.2"}` | Health check |
| `/health` | GET | Same | Alternative health check |
| `/*` | ANY | Same | Catch-all (tất cả request trả về) |

**Lưu ý:** UNO R4 **không có routing** - mọi HTTP request đều trả về cùng response

---

## ⚠️ Giới Hạn & Lưu Ý

### **1. Không Có Routing**
```cpp
// UNO R4 code - Không phân biệt path
if (client) {
  // ... đọc request ...
  
  // ✅ Trả về cùng response cho TẤT CẢ request
  client.println("{\"status\":\"ok\",...}");
}
```

**Nghĩa là:**
- `GET / HTTP/1.1` → `{"status":"ok"}`
- `GET /api/test HTTP/1.1` → `{"status":"ok"}`
- `POST /anything HTTP/1.1` → `{"status":"ok"}`

### **2. Chỉ Dùng Để Health Check**

UNO R4 HTTP server chỉ dùng để:
- ✅ Kiểm tra UNO R4 còn chạy không
- ✅ Xác nhận IP address
- ❌ Không dùng để gửi commands
- ❌ Không dùng để lấy sensor data

### **3. Giao Tiếp 2 Chiều**

Giao tiếp chính:
- **UNO → Flask:** POST `/api/cards/scan` (quét thẻ)
- **Flask → UNO:** Response JSON (success/reject)
- **UNO HTTP Server:** Chỉ để health check

---

## 🔗 Liên Hệ Giữa Các Endpoints

### **UNO R4 Web Server (Port 80)**
```
GET /
→ {"status":"ok","device":"UNO R4 WiFi","ip":"192.168.4.2"}

Dùng cho: Health check (PC kiểm tra UNO R4 còn sống không)
```

### **Flask Backend Server (Port 5000)**
```
POST /api/cards/scan
→ {"success":true/false,"action":"entry"/"exit"/"reject",...}

Dùng cho: Gửi RFID data, nhận lệnh mở/đóng barrier
```

### **React Frontend (Port 3000)**
```
GET /api/cards
→ {"success":true,"cards":[...],"count":N}

Dùng cho: Hiển thị danh sách thẻ trên web
```

---

## 📝 Example: Complete Flow

```
1️⃣ PC quét UNO R4 health
   Request:  GET http://192.168.4.2/
   Response: {"status":"ok","device":"UNO R4 WiFi","ip":"192.168.4.2"}
   ✅ UNO R4 hoạt động bình thường

2️⃣ Người dùng quét thẻ RFID tại readers
   Arduino phát hiện: uid="ABC123", direction="IN"
   
3️⃣ Arduino gửi POST request đến Flask
   Request:  POST http://192.168.4.3:5000/api/cards/scan
   Body:     {"card_id":"ABC123","direction":"IN"}
   
4️⃣ Flask xử lý logic
   - Kiểm tra card trong hệ thống: OK ✅
   - Check status: 0 (ngoài) → Cho phép vào ✅
   - Update status = 1
   - Ghi log: entry
   
5️⃣ Flask trả response
   Response: {
     "success": true,
     "action": "entry",
     "card": {...},
     "message": "Card entry processed"
   }
   
6️⃣ Arduino xử lý response
   - success == true ✅
   - action == "entry" ✅
   - → MỞ BARRIER (servo 90°)
   
7️⃣ Người dùng lái xe vào
   - Barrier đang mở
   - Ultrasonic sensor phát hiện xe
   - Xe đi qua hoàn toàn
   - Barrier tự động đóng

8️⃣ React Frontend cập nhật
   GET /api/cards
   → Thẻ ABC123 bây giờ: status=1 (trong bãi)
   → Hiển thị: "1/10 xe trong bãi"
```

---

## 🎯 Kết Luận

**UNO R4 API Response:**
- ✅ **Port 80:** `{"status":"ok","device":"UNO R4 WiFi","ip":"192.168.4.2"}`
- ✅ **Dùng cho:** Health check + kiểm tra IP
- ✅ **Giao tiếp chính:** HTTP POST đến Flask Server (Port 5000)
- ✅ **Response từ Flask:** Lệnh mở/đóng barrier dựa trên logic

Tóm lại: **UNO R4 là client + minimal server**, chứ không phải full API server như Flask! 🚀
