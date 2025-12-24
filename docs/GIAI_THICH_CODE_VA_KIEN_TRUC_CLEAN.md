# 🔧 Kiến Trúc Kỹ Thuật & Giải Thích Code - Hệ Thống Bãi Đỗ Xe Thông Minh

> **📝 Lưu ý về Phân Tích Chức Năng**: Tài liệu này chứa phân tích chức năng chi tiết dựa trên code thực tế của dự án để đảm bảo độ chính xác 100%.

## 📋 Tổng Quan Kiến Trúc

Hệ thống được xây dựng theo **kiến trúc phân lớp (Layered Architecture)** với **mô hình Client-Server**:

### **🏗️ Các lớp kiến trúc từ trên xuống:**

1. **🌐 LỚP GIAO DIỆN NGƯỜI DÙNG (Presentation Layer)**
   - **Công nghệ**: React TypeScript
   - **Chức năng**: Hiển thị giao diện web, xử lý tương tác người dùng
   - **Giao tiếp**: HTTP API calls tới lớp Logic Nghiệp Vụ

2. **⚙️ LỚP LOGIC NGHIỆP VỤ (Business Logic Layer)**  
   - **Công nghệ**: Python Flask Server
   - **Chức năng**: Xử lý business rules, API endpoints, validation
   - **Giao tiếp**: Nhận HTTP requests từ frontend, thao tác file với Data Layer

3. **💿 LỚP TRUY CẬP DỮ LIỆU (Data Access Layer)**
   - **Công nghệ**: JSON Files + Backup System  
   - **Chức năng**: Lưu trữ dữ liệu thẻ, logs, backup/restore
   - **Giao tiếp**: File I/O operations, được truy cập bởi Business Layer

4. **🔌 LỚP PHẦN CỨNG (Hardware Layer)**
   - **Công nghệ**: Arduino UNO R4 WiFi + ESP32 + RFID Sensors
   - **Chức năng**: Đọc thẻ RFID, điều khiển barriers, phát hiện xe đỗ
   - **Giao tiếp**: HTTP requests tới Backend, WiFi communication

---

## 🎯 Công Nghệ Sử Dụng

### 💻 **Giao Diện Người Dùng (Frontend)**
- **React 18**: Framework JavaScript để xây dựng giao diện
- **TypeScript**: Ngôn ngữ lập trình có kiểm tra kiểu dữ liệu
- **React Router**: Quản lý điều hướng trang (URL routing)
- **Axios**: Thư viện giao tiếp với API server
- **CSS3**: Styling và responsive design

### ⚙️ **Máy Chủ Xử Lý (Backend)**
- **Python 3.8+**: Ngôn ngữ lập trình chính
- **Flask**: Web framework nhẹ để tạo API server
- **Flask-CORS**: Xử lý Cross-Origin Resource Sharing
- **JSON**: Định dạng lưu trữ dữ liệu
- **Threading**: Xử lý đa luồng cho scheduled tasks

### 🔌 **Hardware (Phần Cứng)**
- **Arduino UNO R4 WiFi**: Vi điều khiển chính đọc RFID
- **ESP32**: Vi điều khiển phụ với cảm biến siêu âm
- **RFID RC522**: Module đọc thẻ từ
- **Ultrasonic Sensors**: Cảm biến khoảng cách HC-SR05

---

## 📁 Cấu Trúc Thư Mục Project

```
Baidoxe/
├── 🌐 frontend/                 # Giao diện web (React)
│   ├── src/
│   │   ├── components/          # Các component UI
│   │   ├── types.ts            # Định nghĩa kiểu dữ liệu
│   │   ├── api.ts              # Kết nối với máy chủ
│   │   └── App.tsx             # Component chính
│   ├── public/                 # Static files
│   └── build/                  # Code đã compile
│
├── ⚙️ backend/                  # Máy chủ xử lý (Python)
│   ├── api/                    # API endpoints
│   ├── services/               # Business logic
│   ├── models/                 # Data models
│   ├── utils/                  # Utilities
│   ├── config/                 # Cấu hình
│   └── data/                   # Dữ liệu JSON
│
├── 🔌 hardware/                 # Code cho vi điều khiển
│   ├── esp32_sensors/          # Code ESP32
│   └── uno_r4_wifi/            # Code Arduino UNO R4
│
├── 📋 scripts/                  # Scripts tiện ích
└── 📖 docs/                     # Tài liệu hướng dẫn
```

---

## 🌐 Giao diện người dùng (React) - Giải thích chi tiết

### 📱 **React TypeScript Frontend**

React là **thư viện JavaScript** để xây dựng giao diện người dùng động. Project này sử dụng **React + TypeScript** cho type safety và **React Router** cho navigation giữa các trang.

### 🧩 **Components Chính**

#### 1. **App.tsx - React Router & Shared State Management**

📁 **File: `frontend/src/App.tsx`**

**🏗️ Kiến trúc chính:**
- **BrowserRouter**: Quản lý URL routing cho SPA với 5 pages chính
- **Layout Component**: Container shared state cho toàn bộ app
- **Nested Routes**: Routing system với navigation breadcrumb
- **Centralized State**: Cards, loading, messages, unknownCards được quản lý tập trung

**🧩 Cấu Trúc Components:**
```
App (NotificationProvider)
├── AppWithHooks (useActivityMonitor, useStatsMonitor)
└── Layout (Shared State Container)
    ├── Header (Navigation + Statistics)
    ├── Routes (5 trang: Dashboard, Cards, Parking, Logs, Admin)
    └── Footer (Quick stats)
```

**🔄 Các Hàm Quản Lý State dựa trên code thực tế:**

1. **fetchCards()**: Gọi `parkingApi.getCards()`, cập nhật state, xử lý lỗi
2. **fetchUnknownCards()**: Tải danh sách thẻ lạ từ API
3. **handleAddCard(uid, status)**: Thêm thẻ mới với xử lý lỗi 409 (duplicate)
4. **handleDeleteCard(uid)**: Xóa thẻ với hộp thoại xác nhận
5. **handleReload()**: Tải lại dữ liệu từ file JSON với parkingApi.reload()

**📊 Tính Năng Real-time:**
- **Auto-refresh**: setInterval(5000ms) cho trang cards
- **Tính toán thống kê**: Lọc cards theo status để tính inside/outside count
- **Dynamic title**: Tiêu đề document thay đổi theo route
- **Tự động xóa thông báo**: setTimeout(3000ms) để xóa thông báo

**🎯 Navigation System:**
- **5 Routes**: /, /dashboard, /cards, /parking, /logs, /admin
- **Active state tracking**: CSS classes dựa trên location.pathname
- **Breadcrumb system**: Dynamic breadcrumb với getBreadcrumb()
- **Redirect logic**: "/" redirect to "/dashboard"

**⚡ Performance Optimizations:**
- **useCallback**: fetchCards, fetchUnknownCards để prevent re-renders
- **Conditional effects**: Chỉ fetch data khi ở cards page
- **Shared props pattern**: Object destructuring cho component props

#### 2. **Dashboard.tsx - Trang Tổng Quan Hệ Thống**

📁 **File: `frontend/src/components/Dashboard.tsx`**

**🎯 Chức năng chính dựa trên code thực tế:**

**📊 Data Management:**
- **DashboardStats Interface**: `total_cards`, `inside_parking`, `outside_parking`, `occupancy_rate`
- **LogStats Interface**: `count` + `logs[]` với chi tiết `id`, `timestamp`, `card_id`, `action`, `details`
- **State Management**: 5 useState hooks cho stats, logs, loading, error, lastUpdate

**🔄 API Integration:**
```javascript
fetchStats() // Parallel API calls:
├── GET /api/cards/statistics     // Thống kê tổng quan
└── GET /api/cards/logs?limit=10  // 10 log gần nhất
```

**⚡ Real-time Features:**
- **Auto-refresh**: `setInterval(30000ms)` với cleanup trong useEffect
- **Manual refresh**: Button onClick={fetchStats} với disabled state
- **Live timestamp**: `lastUpdate.toLocaleTimeString('vi-VN')`
- **Error handling**: Try-catch với error state display

**🎨 UI Components Structure:**
```
Dashboard
├── Header (Title + Refresh Controls + Last Update Time)
├── Error Message (Conditional render)
├── Stats Grid (4 cards)
│   ├── Total Cards (📋)
│   ├── Inside Parking (🚗)  
│   ├── Outside Parking (🏠)
│   └── Occupancy Rate (📈)
├── Occupancy Bar (Visual progress với dynamic width)
├── Recent Activity (10 logs với color-coded actions)
└── Quick Actions (Backup + Fix Data buttons)
```

**🔧 Helper Functions:**
- **getActionColor()**: Maps actions to Bootstrap colors (entry=green, exit=red, scan=blue, unknown=yellow)
- **getActionIcon()**: Maps actions to emojis (🚗➡️, 🚗⬅️, 📱, ❓)
- **formatTimestamp()**: Convert ISO to Vietnamese locale format

**🛠️ Quick Actions với API Calls:**
1. **Backup Button**: `POST /api/cards/backup` với success/error alerts
2. **Fix Data Button**: `POST /api/cards/fix-data` với confirmation dialog và fetchStats() refresh

**📱 Responsive Design Features:**
- **Loading state**: Full-page loading với "Đang tải dữ liệu dashboard..."
- **Empty state**: "Chưa có hoạt động nào" khi logs rỗng
- **Error resilience**: Optional chaining `stats?.total_cards || 0` để tránh crash
- **Color coding**: Dynamic styling cho activity items dựa trên action type

**🔄 Performance Optimizations:**
- **Promise.all()**: Parallel API calls thay vì sequential
- **Cleanup interval**: Proper cleanup trong useEffect return
- **Conditional rendering**: Chỉ render UI khi có data hoặc đang loading

#### 3. **api.ts - Kết Nối Máy Chủ**

📁 **File: `frontend/src/api.ts`**

**🧠 Smart URL Detection System:**
```javascript
getApiBaseUrl() // Intelligent backend discovery:
├── localhost/127.0.0.1 → http://localhost:5000    (Development)
└── Network IP → http://{current_ip}:5000          (Production)
```

**🔄 Fallback System với Retry Logic:**
```javascript
FALLBACK_URLS = [
  'http://192.168.4.3:5000',  // Primary IoT network IP
  'http://127.0.0.1:5000',    // Local loopback
  'http://localhost:5000'     // Local hostname
]
```

**⚙️ Axios Instance Configuration:**
- **Base URL**: Dynamic detection
- **Timeout**: 10 seconds
- **Headers**: `application/json`
- **Request Interceptor**: Console logging với format `🚀 API Request: {url} {method}`
- **Response Interceptor**: Success/error logging + automatic fallback retry

**🔄 Advanced Retry Mechanism:**
- **Error Detection**: `ECONNREFUSED` || `ERR_NETWORK`
- **Fallback Loop**: Iterate through FALLBACK_URLS
- **Logging**: Console output cho debugging (`🧪 Đang thử:`, `✅ Fallback thành công`)
- **Skip Logic**: Avoid duplicate URL attempts

**📡 API Methods dựa trên Backend Endpoints:**

**1. Card Management:**
- **getCards()**: `GET /api/cards` → Convert array to Record<uid, ParkingCard>
- **addCard(uid, status)**: `POST /api/cards` với status mapping (0='active', 1='parked')
- **deleteCard(uid)**: `DELETE /api/cards/{uid}` với boolean return
- **reload()**: `POST /api/reload` để reload từ JSON file

**2. Unknown Cards System:**
- **getUnknownCards()**: `GET /api/cards/unknown` → Array of unknown cards
- **clearUnknownCards()**: `DELETE /api/cards/unknown` → Clear all
- **removeUnknownCard(uid)**: `DELETE /api/cards/unknown/{uid}` → Remove specific

**3. Statistics & Monitoring:**
- **getStatistics()**: `GET /api/cards/statistics` → Dashboard metrics
- **getLogs(params)**: `GET /api/cards/logs` với query parameters:
  ```javascript
  params: {
    action?: string,    // Filter by action type
    card_id?: string,   // Filter by card ID
    limit?: number,     // Max records (default: 50)
    offset?: number     // Skip records (default: 0)
  }
  ```

**4. Parking Slots Integration:**
- **getParkingSlots(endpoint)**: `GET /api/parking-slots` (customizable endpoint)
- **resetParkingSlots()**: `POST /api/parking-slots/reset` → Reset all slots to empty

**🛡️ Type Safety Features:**
- **Generic Response Types**: `ApiResponse<T>`, `ParkingCard`, etc.
- **Status Mapping**: Object-based mapping (0/1 → 'active'/'parked')
- **Return Type Consistency**: Boolean success/failure cho CRUD operations
- **Error Propagation**: Proper TypeScript error handling

**🚀 Performance & Reliability:**
- **Connection Pooling**: Axios instance reuse
- **Request Deduplication**: Automatic via Axios
- **Error Boundaries**: Try-catch được handle ở component level
- **Network Resilience**: Multi-URL fallback strategy
- **Debug Friendly**: Comprehensive console logging cho development

**🔧 URL Construction Patterns:**
- **Static Endpoints**: Direct string paths
- **Dynamic Parameters**: Template literals với validation
- **Query Strings**: URLSearchParams construction cho filters
- **RESTful Design**: Consistent HTTP verbs (GET/POST/DELETE)

### 🔄 **Luồng dữ liệu (Data Flow)**

```
Người dùng nhấn nút → Component event handler → API call → Backend processing → JSON response → State update → UI re-render
```

**Ví dụ thực tế - Thêm thẻ mới:**
1. User nhập UID và nhấn "Thêm thẻ"
2. `AddCardForm` component bắt sự kiện submit
3. Gọi `parkingApi.addCard(uid, status)`
4. Gửi HTTP POST đến backend `/api/cards`
5. Backend xử lý và trả về response
6. Frontend nhận response và cập nhật UI
7. Hiển thị thông báo thành công/thất bại

---

## ⚙️ Máy chủ xử lý (Python Flask) - Giải thích chi tiết

### 🐍 **Python Flask Backend**

Flask là **web framework** cho Python, tạo RESTful API endpoints để xử lý requests từ frontend và hardware. Backend này implement **Service Layer Pattern** và **Repository Pattern** cho business logic.

### 🏗️ **Kiến Trúc Backend**

#### 1. **app.py - Application Factory**

**Chức năng**:
- Tạo và cấu hình Flask application
- Thiết lập CORS để frontend có thể gọi API
- Đăng ký các API endpoints
- Xử lý lỗi toàn cục

**🏭 Flask Application Factory Pattern dựa trên code thực tế:**

**📊 Core App Architecture:**
```python
create_app() → Flask App Factory:
├── Flask instance setup với frontend paths (React build)
├── Configuration loading từ config classes  
├── CORS initialization với security whitelist
├── Blueprint registration (cards, parking_slots, system APIs)
├── Comprehensive error handling cho tất cả HTTP codes
├── Request/response logging với debug mode
├── Frontend serving (React SPA support + static files)  
├── Health endpoints cho monitoring
└── Background scheduler cho automated tasks
```

**🔧 Advanced Features:**

**1. Smart Frontend Serving:**
- **React SPA Support**: serve index.html cho React Router paths
- **Static Files**: CSS/JS/images với proper MIME types
- **Fallback Logic**: API info khi frontend build không có
- **Error Recovery**: Graceful degradation khi frontend missing

**2. Production-Ready Error Handling:**
- **HTTP 404/405/415/500**: Structured JSON error responses
- **Generic Exception Handler**: Catch-all với proper logging
- **Vietnamese Messages**: User-friendly error messages
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, XSS Protection

**3. Development & Monitoring Tools:**
- **Debug Logging**: Detailed request/response logging trong dev mode
- **Health Endpoints**: `/health`, `/api`, `/api/endpoints` cho monitoring
- **Endpoint Discovery**: Auto-generate API documentation
- **Performance Tracking**: Request timing và error rates

**4. Background Services Integration:**
- **Automated Scheduler**: scheduled_tasks.start_scheduler() khi app khởi động
- **Data Directory Setup**: Auto-create required JSON files nếu missing
- **Graceful Startup**: Error handling trong initialization phase

#### 2. **API Endpoints (api/cards.py)**

📁 **File: `backend/api/cards.py`**

**Chức năng chính:**
- **CRUD operations**: Create, Read, Update, Delete cho parking cards
- **Hardware integration**: Endpoints cho Arduino/ESP32 communication
- **Statistics**: Endpoints cung cấp thống kê hệ thống
- **Error handling**: Comprehensive validation và error responses

**🏗️ Cards API Architecture dựa trên code thực tế:**

**📡 RESTful Endpoints với Comprehensive Functionality:**
```python
Card Management CRUD:
├── GET /api/cards → List all cards với count
├── GET /api/cards/<id> → Single card detail với validation
├── POST /api/cards → Create card với status mapping (active/parked/inactive)
├── PUT /api/cards/<id> → Update card với data validation
├── DELETE /api/cards/<id> → Delete card với confirmation
└── POST /api/cards/<id>/status → Update parking status (0/1)

Hardware Integration:
├── POST /api/cards/scan → Arduino/ESP32 RFID processing
│   ├── Direction-aware logic (IN/OUT readers)
│   ├── Status validation (prevent double entry/exit)
│   ├── Unknown card logging và rejection
│   └── Real-time barrier control responses

Analytics & Monitoring:
├── GET /api/cards/statistics → Dashboard metrics calculation
├── GET /api/cards/logs → Activity logs với filtering
│   ├── Query params: card_id, action, limit, offset
│   ├── Action mapping: entry, exit, scan, unknown, etc.
│   └── Pagination support cho large datasets
└── GET /api/cards/unknown → Unknown cards management

Admin Operations:
├── POST /api/cards/fix-data → Auto-fix negative duration data
├── POST /api/cards/backup → Manual backup trigger
├── POST /api/cards/reload → Reload from JSON files
└── DELETE /api/cards/unknown → Clear unknown cards list
```

**🧠 Smart Hardware Integration Logic:**
```python
Card Scan Processing (/scan endpoint):
├── Input validation: JSON format + card_id required
├── Direction Logic:
│   ├── "IN" reader: Only allow entry (status 0→1)
│   ├── "OUT" reader: Only allow exit (status 1→0)  
│   └── Fallback: Toggle status if direction missing
├── State Validation:
│   ├── Prevent double entry (already parked)
│   ├── Prevent invalid exit (already outside)
│   └── Return specific error messages
├── Unknown Card Handling:
│   ├── Auto-add to unknown_cards.json
│   ├── Log detection với metadata
│   └── Return 403 Forbidden với card_id
└── Response Format:
    ├── Success: action, direction, parking_status
    └── Error: specific reason, current status
```

**🛡️ Advanced Validation & Error Handling:**
```python
Data Validation Pipeline:
├── ValidationHelper.validate_card_id() → Format checking
├── ValidationHelper.clean_card_id() → Normalize UID
├── ValidationHelper.validate_card_data() → Complete data validation
├── Content-Type checking → application/json required
├── Request body validation → Structured error responses
└── HTTP Status Codes → Proper REST semantics (200,201,400,403,404,500)

Error Response Structure:
{
  "success": false,
  "error": "Error type",
  "message": "Vietnamese user message", 
  "errors": [...],  // Validation details
  "action": "reject", // For hardware responses
  "status_code": 400
}
```

**📊 Statistics & Logging Integration:**
```python
Real-time Metrics:
├── card_service.get_statistics() → total, inside, outside, occupancy_rate
├── Automatic logging mọi operations:
│   ├── LogAction.CARD_ENTRY/EXIT cho status changes
│   ├── LogAction.CARD_SCAN cho hardware interactions
│   ├── LogAction.UNKNOWN_CARD cho unregistered cards
│   └── LogAction.CARD_CREATED/DELETED cho admin operations
└── Activity timeline với timestamps và metadata
```

#### 3. **Business Logic (services/card_service.py)**

📁 **File: `backend/services/card_service.py`**

**Chức năng chính:**
- **CRUD operations** cho parking cards
- **Quản lý unknown cards** (thẻ lạ)
- **Tính toán thống kê** hệ thống
- **Auto-backup** sau các thay đổi
- **Logging** cho audit trail
- **Validation** và error handling

**🏗️ CardService Class Architecture dựa trên code thực tế:**

**🔧 Dependency Management:**
```python
class CardService:
    def __init__(self):
        self.file_manager = FileManager()
        # Lazy Loading Pattern để tránh circular imports:
        self._backup_service = None  # → BackupService
        self._log_service = None     # → CardLogService
    
    @property backup_service / log_service:
        # Dynamic import chỉ khi cần thiết
        if self._service is None:
            from services.xxx import XxxService
            self._service = XxxService()
        return self._service
```

**📊 Data Operations với Error Handling:**

**1. Read Operations:**
```python
get_all_cards() → Dict[str, ParkingCard]:
├── file_manager.read_json(CARDS_FILE, default={})
├── _parse_cards_from_dict() với nested data support
│   ├── Handle both: {"cards": {...}} và {...} formats
│   ├── ParkingCard.from_dict() cho mỗi item
│   └── Skip invalid cards với warning log
└── Return: Dict[uid → ParkingCard object]

get_card(uid) → Tuple[bool, Optional[Dict]]:
├── get_all_cards()
├── Check existence trong dict
└── Return: (success, card.to_dict() or None)
```

**2. Write Operations với Atomic File Handling:**
```python
create_card(uid, status=0) → Tuple[bool, str, Optional[ParkingCard]]:
├── Validation: Check duplicate uid
├── new_card = ParkingCard(uid, status)  
├── Serialize: {uid: card.to_dict() for all cards}
├── file_manager.write_json(max_backups=5) 
├── Logging: LogAction.CARD_CREATED với metadata
└── Return: (success, vietnamese_message, card_object)

delete_card(uid) → Tuple[bool, str]:
├── Validation: Check existence
├── del cards_dict[uid]
├── Atomic write toàn bộ dict
├── Logging: LogAction.CARD_DELETED
└── Vietnamese success/error messages
```

**3. Business Logic Operations:**
```python
update_card_status(uid, new_status) → Tuple[bool, str, Optional[Dict]]:
├── Load card from dict
├── card.update_status(new_status) # Delegate to model
├── Check result["success"] từ model
├── Atomic write nếu success
├── Smart logging dựa trên action:
│   ├── new_status=1 → LogAction.CARD_ENTRY  
│   └── new_status=0 → LogAction.CARD_EXIT
└── Return updated card.to_dict()

get_statistics() → Dict[str, Any]:
├── Load all cards
├── Calculations:
│   ├── total_cards = len(cards)
│   ├── inside_count = sum(status == 1)  
│   ├── outside_count = total - inside
│   └── occupancy_rate = (inside/total * 100) if total > 0 else 0
└── Return metrics dict cho Dashboard
```

**🔍 Unknown Cards Management:**
```python
Unknown Cards System:
├── add_unknown_card(uid, metadata) với normalization
├── get_unknown_cards() → List[Dict] từ JSON file
├── remove_unknown_card(uid) với filter operation
├── Duplicate detection dựa trên normalized UID
└── Auto-logging mọi unknown card events
```

**🛡️ Error Handling & Resilience:**
```python
Comprehensive Exception Handling:
├── Try-catch wrapper cho mọi methods
├── Detailed logging: logger.error/warning/info 
├── Vietnamese user messages vs English log messages
├── Graceful degradation: Return empty {} instead of crash
├── Tuple return pattern: (success: bool, message: str, data: Optional)
└── Continue processing on non-critical errors (log parsing)
```

**📁 File Management Integration:**
```python
FileManager Integration:
├── write_json(file, data, max_backups=5) # Atomic writes
├── read_json(file, default_value={}) # Safe reads  
├── Auto-backup sau mỗi modification
├── Backup rotation để prevent disk full
└── Error recovery từ backup nếu main file corrupt
```

**🔄 Logging & Audit Trail:**
```python
Integrated Logging System:
├── LogAction enums: CARD_CREATED, CARD_DELETED, CARD_ENTRY, CARD_EXIT, UNKNOWN_CARD
├── Metadata tracking cho mọi operations
├── Failure isolation: Log service lỗi không break main operation
├── Structured logging với context (uid, action, details)
└── Audit trail cho compliance và debugging
```

**⚡ Performance Optimizations:**
- **Lazy Loading**: Services chỉ load khi cần
- **Batch Operations**: Single file write cho multiple card changes  
- **In-memory Processing**: Load → process → save pattern
- **Error Isolation**: Individual card parsing errors không affect others
- **Efficient Statistics**: Single pass calculation thay vì multiple queries

#### 4. **Data Models (models/card.py)**

📁 **File: `backend/models/card.py`**

**🏗️ ParkingCard Class Architecture:**
```python
class ParkingCard:
    # Core Attributes:
    uid: str              # RFID unique ID (normalized: upper + strip)
    status: int          # 0=outside, 1=inside parking
    entry_time: str      # ISO timestamp when entering
    exit_time: str       # ISO timestamp when exiting  
    created_at: str      # ISO timestamp when card created
    parking_duration: dict # Calculated duration object
```

**⚡ Các phương thức cốt lõi dựa trên code thực tế:**

**1. Constructor & Xử lý dữ liệu:**
- **__init__(uid, status=0, ...)**: Tự động chuẩn hóa UID (`upper().strip()`)
- **Tính toán tự động**: Gọi `_calculate_parking_duration()` trong constructor
- **Timestamps mặc định**: `created_at` mặc định là thời gian UTC ISO hiện tại

**2. Hệ thống quản lý thời gian:**
```python
_calculate_parking_duration():
├── Parse ISO timestamps (xử lý hậu tố 'Z')
├── Các nhánh logic:
│   ├── Đã ra (exit_time + status=0) → thời lượng từ vào đến ra
│   ├── Vẫn bên trong (status=1) → từ vào đến thời điểm hiện tại  
│   └── Không có dữ liệu hợp lệ → parking_duration = None
├── Kiểm tra: Thời lượng âm → xóa exit_time không hợp lệ
└── Định dạng đầu ra: {"total_seconds", "hours", "minutes", "display"}
```

**Tính năng thời gian thực:**
- **Thời lượng trực tiếp**: Xe bên trong hiển thị chỉ báo "(hiện tại)"
- **refresh_parking_duration()**: Cập nhật thời lượng cho thẻ status=1
- **Tự động sửa dữ liệu sai**: Reset exit_time nếu entry > exit

**3. Quản lý trạng thái:**
```python
update_status(new_status) → Trả về:
{
  "success": bool,
  "message": str,       # Thông báo người dùng tiếng Việt
  "action": str,        # "entry"/"exit"/"no_change" 
  "old_status": int,
  "new_status": int,
  "timestamp": str,     # ISO timestamp
  "parking_duration": dict
}
```

**Logic nghiệp vụ:**
- **Vào (status→1)**: Đặt entry_time, xóa exit_time, xóa duration
- **Ra (status→0)**: Đặt exit_time, tính toán duration cuối cùng
- **Không thay đổi**: Trả về success=False với thông báo phù hợp

**4. Serialization & Validation:**
```python
# Serialization:
to_dict() → Trường có điều kiện (chỉ include nếu có value)
from_dict(data) → Class method constructor

# Validation:  
validate() → {"valid": bool, "errors": list}
├── UID: không rỗng, tối thiểu 4 ký tự
├── Status: phải là 0 hoặc 1
└── Timestamps: định dạng ISO hợp lệ
```

**🔧 Tính năng toàn vẹn dữ liệu:**
- **Chuẩn hóa UID**: Tự động uppercase + loại bỏ khoảng trắng
- **Xử lý ISO Timestamp**: Hỗ trợ cả hậu tố 'Z' và '+00:00'
- **Khôi phục lỗi**: Thời lượng âm không hợp lệ → tự động sửa dữ liệu
- **Serialization có điều kiện**: Chỉ bao gồm các trường có giá trị
- **An toàn kiểu dữ liệu**: Validation toàn diện cho tất cả trường

**📊 Logic tính toán thời lượng:**
```python
Định dạng hiển thị thời lượng:
├── Giờ + Phút: "2 giờ 30 phút (hiện tại)"
├── Chỉ phút: "45 phút (hiện tại)"  
├── Dữ liệu không hợp lệ: "Dữ liệu lỗi - thời gian không hợp lệ (đã reset)"
└── Không có dữ liệu: None
```

**🛡️ Xử lý lỗi & Độ tin cậy:**
- **Bắt ValueError**: Phân tích ISO timestamp không hợp lệ
- **Xử lý AttributeError**: Trường timestamp None/thiếu
- **Khôi phục dữ liệu hỏng**: Tự động reset thời gian thoát không hợp lệ
- **Giảm hiệu suất nhẹ nhàng**: Trường thiếu không làm hỏng chức năng
- **Thông báo thân thiện**: Thông báo lỗi tiếng Việt cho validation

**🎯 Triển khai quy tắc nghiệp vụ:**
- **Nguồn sự thật duy nhất**: Status quyết định logic trạng thái hiện tại
- **Lịch sử bất biến**: Created_at không bao giờ thay đổi sau khởi tạo
- **Độ chính xác thời gian thực**: Duration tự động cập nhật cho xe đã đỗ
- **Audit trail**: Tất cả thay đổi trạng thái trả về log hoạt động chi tiết

---

## 🔧 Cấu Hình Hệ Thống

### ⚙️ **Backend Configuration**

#### 1. **Configuration Management (config/config.py)**

📁 **File: `backend/config/config.py`**

**Chứa tất cả cấu hình:**
- **File paths** và directories
- **Network configuration** (API server, ESP32, UNO R4)
- **Auto IP detection** cho UNO R4 WiFi network
- **Mock server settings** cho testing
- **Flask app configurations**

**🏗️ Configuration Architecture dựa trên code thực tế:**

**📁 Path Management với Pathlib:**
```python
File Structure:
├── BASE_DIR = Path(__file__).parent.parent  # backend/
├── DATA_DIR = BASE_DIR / "data" 
├── CARDS_FILE = DATA_DIR / "cards.json"
├── UNKNOWN_CARDS_FILE = DATA_DIR / "unknown_cards.json"  
└── FRONTEND_BUILD_DIR = BASE_DIR.parent / "frontend" / "build"
```

**🌐 Smart Network Detection System:**
```python
detect_api_host() → Dynamic IP Detection:
├── Create UDP socket to UNO R4 (192.168.4.2:80)
├── Get local IP từ socket.getsockname()[0] 
├── Success: Return actual network interface IP
├── Failure: Fallback to "0.0.0.0" (bind all interfaces)
└── Console feedback: "🎯 Server sẽ chạy trên: {ip}"
```

**🔧 IoT Network Configuration:**
```python
Hardware Network Topology:
├── UNO R4 WiFi AP:
│   ├── IP: "192.168.4.2" (Gateway + Access Point)
│   ├── SSID: "UNO-R4-AP" 
│   └── Role: Network hub cho toàn bộ hệ thống
├── Backend Server:
│   ├── IP: detect_api_host() → Auto-detected
│   ├── Port: 5000
│   └── Role: API server + Web interface  
└── ESP32 Sensors:
    ├── IP: "192.168.4.5"
    ├── Port: 80
    ├── Timeout: 10s cho HTTP requests
    └── DETECTION_THRESHOLD: 10cm cho parking detection
```

**⚙️ Application Configuration Classes:**
```python
Configuration Hierarchy:
├── Config (Base):
│   ├── SECRET_KEY: Environment variable hoặc default
│   ├── DEBUG: DEBUG_MODE boolean
│   ├── HOST: detect_api_host() result
│   └── PORT: 5000
├── DevelopmentConfig(Config):
│   └── DEBUG = True (Override)
└── ProductionConfig(Config):
    ├── DEBUG = False (Override)  
    └── SECRET_KEY: Production-specific hoặc env var

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig, 
    'default': DevelopmentConfig  # Fallback
}
```

**🔄 Backup & Logging Configuration:**
```python
System Maintenance Settings:
├── BACKUP_INTERVAL = 3600    # 1 hour (seconds)
├── MAX_BACKUPS = 24          # Keep 24 backups (1 day retention)
├── Auto-cleanup: Rotate old backups để prevent disk full
└── Integration: Used by BackupService cho scheduled tasks
```

**🎯 Các mẫu thiết kế chính:**

**1. Cấu hình động:**
- **Phát hiện thời gian chạy**: Khám phá giao diện mạng thay vì IP cứng
- **Nhận thức môi trường**: Cấu hình DEV vs PROD
- **Chiến lược dự phòng**: Giảm hiệu suất nhẹ nhàng khi phát hiện thất bại

**2. Tính năng đặc trưng IoT:**
- **Ánh xạ IP Hardware**: IP được định nghĩa trước cho ESP32, UNO R4
- **Quản lý Timeout**: Network timeout cho kết nối IoT không ổn định
- **Ngưỡng vật lý**: Khoảng cách phát hiện cho cảm biến siêu âm

**3. Tích hợp hệ thống file:**
- **Đường dẫn đa nền tảng**: Pathlib thay vì nối chuỗi string
- **Giải quyết đường dẫn tương đối**: Dynamic resolution từ vị trí module
- **Cấu trúc thư mục dữ liệu**: Phân tách có tổ chức giữa code và data

**4. Cân nhắc bảo mật:**
- **Biến môi trường**: SECRET_KEY từ env thay vì hardcode
- **Phân tách phát triển**: Khác biệt rõ ràng giữa dev và prod
- **Dự phòng mặc định**: Giá trị mặc định an toàn khi thiếu env vars

**🔍 Tính năng sẵn sàng sản xuất:**
- **Console Logging**: Phản hồi trực quan cho phát hiện mạng
- **Xử lý lỗi**: Try-catch trong detect_api_host()
- **Ánh xạ cấu hình**: Chuyển đổi dễ dàng giữa các môi trường
- **Tài liệu**: Docstrings và comments toàn diện

#### 2. **Security Configuration (config/cors.py)**

📁 **File: `backend/config/cors.py`**

**🛡️ CORS Configuration dựa trên code thực tế:**

```python
def init_cors(app) → Configured Flask app:
    CORS(app, 
        origins=[                        # Whitelist origins:
            "http://localhost:3000",     # React dev server
            "http://127.0.0.1:3000",    # React dev (loopback)
            "http://localhost:5000",     # Production build served by Flask
            "http://127.0.0.1:5000",    # Production (loopback)  
            "http://192.168.4.3:5000"   # IoT network access
        ],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True        # Enable cookie/session support
    )
```

**🔐 Tính năng bảo mật:**

**1. Validation nguồn gốc:**
- **Phát triển**: localhost:3000 cho React dev server
- **Sản xuất**: localhost:5000 cho ứng dụng React được build do Flask phục vụ
- **Truy cập mạng**: 192.168.4.3:5000 cho thiết bị IoT và network clients
- **Dual Loopback**: Cả localhost và 127.0.0.1 cho khả năng tương thích

**2. Điều khiển HTTP Methods:**
- **Hỗ trợ RESTful**: GET, POST, PUT, DELETE cho CRUD operations
- **Preflight**: OPTIONS cho các yêu cầu CORS phức tạp
- **Bảo mật**: Chỉ cho phép các phương thức cần thiết, không có wildcard

**3. Quản lý Headers:**
- **Content-Type**: Kích hoạt giao tiếp JSON
- **Authorization**: Hỗ trợ cho các tính năng authentication tương lai
- **Không Wildcard**: Danh sách header rõ ràng thay vì allow-all

**4. Hỗ trợ Credentials:**
- **supports_credentials=True**: Kích hoạt cookies, sessions
- **Sẵn sàng tương lai**: Cho triển khai authentication/authorization
- **An toàn**: Kết hợp với whitelist nguồn gốc cho bảo mật

### 🌐 **Network Configuration**

#### **Kế hoạch địa chỉ IP**:
- **192.168.4.2**: Arduino UNO R4 WiFi (Gateway + Access Point)
- **192.168.4.3**: Python Flask Server  
- **192.168.4.5**: ESP32 Sensors
- **192.168.4.x**: Thiết bị client (laptops, phones)

#### **Phân bổ Port**:
- **Port 80**: ESP32 HTTP server, giao diện web Arduino
- **Port 5000**: Python Flask API server
- **Port 3000**: React development server

---

## 💾 Data Models & JSON Schema

### 💾 **Parking Card Data Model**

**💾 Cấu trúc dữ liệu JSON dựa trên code thực tế:**

**🗂️ Định dạng lưu trữ thẻ (`backend/data/cards.json`):**
```json
{
  "CARD_UID": {
    "uid": "CARD_UID",              // UID đã chuẩn hóa uppercase
    "status": 0,                    // 0=bên ngoài, 1=đã đỗ
    "entry_time": "ISO_TIMESTAMP",  // Khi vào (tùy chọn)
    "exit_time": "ISO_TIMESTAMP",   // Khi ra (tùy chọn) 
    "created_at": "ISO_TIMESTAMP",  // Thời gian tạo lần đầu
    "parking_duration": {           // Được tính bởi model
      "total_seconds": 3600,
      "hours": 1,
      "minutes": 0,
      "display": "1 giờ 0 phút"
    }
  }
}
```

**📝 Ví dụ thực tế từ Backup File:**
```json
{
  "ALIEN888": {
    "uid": "ALIEN888",
    "status": 0,
    "created_at": "2025-10-06T19:24:07.002259+00:00"
  }
}
```

**🔄 Logic ParkingCard Model dựa trên models/card.py:**
```python
Quy tắc xử lý dữ liệu:
├── Chuẩn hóa UID: .upper().strip() để đảm bảo nhất quán
├── Trường tự động tính:
│   ├── created_at: UTC ISO timestamp nếu không có
│   ├── parking_duration: Tính từ entry_time và status
│   └── Cập nhật thời gian thực: Live duration cho xe đang đỗ
├── Quản lý trạng thái:
│   ├── 0 = Bên ngoài bãi đỗ (có sẵn)
│   ├── 1 = Bên trong bãi đỗ (đã đỗ)
│   └── Thay đổi trạng thái kích hoạt theo dõi thời gian
└── Quy tắc validation:
    ├── UID tối thiểu 4 ký tự
    ├── Status phải là 0 hoặc 1
    └── Timestamps phải có định dạng ISO hợp lệ
```

**📊 Additional JSON Files:**
```json
// unknown_cards.json - Unregistered RFID detections
[
  {
    "uid": "UNKNOWN123",
    "first_seen": "ISO_TIMESTAMP",
    "detection_count": 5,
    "source": "uno_r4"
  }
]

// card_logs.json - Activity audit trail  
[
  {
    "id": "unique_id",
    "timestamp": "ISO_TIMESTAMP",
    "card_id": "CARD_UID",
    "action": "entry|exit|scan|unknown|created",
    "details": {...}
  }
]
```

**🎯 Key Design Patterns:**

**1. Dictionary-based Storage:** Cards stored as `{uid: card_object}` để O(1) lookup
**2. Conditional Serialization:** chỉ include fields có value trong JSON
**3. Auto-backup System:** Backup rotation với timestamps để data protection
**4. Atomic Operations:** File writes với error recovery để prevent corruption

**Giải thích fields chi tiết:**
- **uid**: Unique identifier của thẻ RFID
- **status**: Trạng thái (0=ngoài bãi, 1=trong bãi)
- **entry_time**: Timestamp ISO khi xe vào bãi
- **exit_time**: Timestamp ISO khi xe ra bãi (nullable)
- **created_at**: Timestamp tạo thẻ lần đầu
- **parking_duration**: Object chứa thông tin thời lượng đỗ xe

---

## 🔌 Lớp phần cứng - Vi điều khiển

### 🎯 **Arduino UNO R4 WiFi**

📁 **File: `hardware/uno_r4_wifi/uno_r4_wifi.ino`**

**Chức năng chính:**
- **Dual RFID readers**: IN và OUT traffic control
- **Servo barrier control**: Non-blocking state machine
- **WiFi Access Point**: Network hub cho toàn bộ hệ thống
- **Vehicle detection**: Ultrasonic sensors cho safety

**Architecture highlights:**
- **State Machine Pattern**: Non-blocking barrier control
- **Dual RFID Processing**: Parallel readers với independent timing
- **WiFi AP Configuration**: Static IP setup và network management
- **Safety Logic**: Vehicle detection trước khi đóng barrier

**🏗️ Arduino UNO R4 WiFi Implementation dựa trên uno_r4_wifi.ino:**

**📡 Hardware Configuration:**
```cpp
Dual RFID System:
├── IN Reader (RC522): SS=10, RST=9, SPI shared
├── OUT Reader (RC522): SS=7, RST=8, SPI shared
├── Servo Barriers: IN=Pin5, OUT=Pin6 (0°=closed, 90°=open)
├── Ultrasonic Sensors: IN(TRIG=3,ECHO=4), OUT(TRIG=2,ECHO=A0)
└── WiFi AP: SSID="UNO-R4-AP", IP=192.168.4.2, Password="12345678"

Component Integration:
├── SPI Bus sharing giữa dual RFID readers
├── Non-blocking servo control với millis() timing  
├── Vehicle detection với noise filtering (3 stable readings)
└── Web server port 80 cho health monitoring
```

**🔄 Multi-Reader Processing Architecture:**
```cpp
Parallel RFID Management:
├── Independent timing: 100ms intervals cho mỗi reader
├── UID memory system: 3-second cooldown để prevent duplicate reads
├── Direction-aware processing: IN vs OUT logic separation
├── HTTP POST to backend: /api/cards/scan với direction field
└── Response-based barrier control: chỉ mở khi backend success

RFID Read Cycle:
1. readRFID(rfidIn, "IN") → Check for card presence
2. Compare với lastUID_IN → Skip duplicates trong 3s window  
3. sendRFIDToServer(uid, "IN") → HTTP POST với JSON payload
4. Parse response → openBarrier() nếu success=true
5. Parallel processing cho OUT reader với independent timing
```

**⚡ Performance & Safety Features:**
```cpp
System Optimizations:
├── Non-blocking design: State machines thay vì delay() calls
├── Minimal loop delay: 10ms để responsive control
├── HTTP timeout: 1s thay vì 3s để reduce latency
├── Memory management: String cleanup sau HTTP calls
└── Error isolation: Network failures không break local control

Safety Systems:
├── Vehicle detection trước barrier closure
├── Emergency timeout: 30s maximum open time
├── Stable reading requirement: 3 consecutive detections  
├── Final safety check: 200ms delay + re-scan
└── Force override: openBarrier() có thể interrupt closing
```

#### **State Machine Logic - Barrier Control**

**Barrier States:**
- **IDLE**: Chờ lệnh mở từ valid RFID
- **OPENING**: Servo đang mở (2 seconds)
- **WAITING_VEHICLE**: Chờ xe đi vào detection zone
- **VEHICLE_PRESENT**: Xe đang trong zone
- **CLOSING**: Servo đang đóng
- **TIMEOUT_CLOSING**: Tự động đóng sau timeout

**🎯 State Machine Implementation dựa trên uno_r4_wifi.ino:**

**📊 BarrierState Enum & Control Structure:**
```cpp
enum BarrierState {
  IDLE,               // Barrier đóng, sẵn sàng nhận lệnh
  OPENING,            // Đang mở barrier (2 giây)
  WAITING_VEHICLE,    // Mở xong, chờ xe vào zone
  VEHICLE_PRESENT,    // Xe đã vào, chờ xe đi qua
  CLOSING,            // Đang đóng barrier (2 giây)
  TIMEOUT_CLOSING     // Đóng khẩn cấp do timeout
};

struct BarrierControl {
  BarrierState state;
  unsigned long stateStartTime;    // Timing cho transitions
  int presentCount, absentCount;   // Noise filtering counters
  bool vehicleDetected;           // Current detection status
  Servo* servo;                   // Servo motor control
  int trigPin, echoPin;          // Ultrasonic sensor pins
  String name;                   // "IN" hoặc "OUT" identifier
};
```

**🔄 State Transition Logic trong updateBarrier():**
```cpp
State Flow Management:
├── IDLE → OPENING:
│   ├── Trigger: openBarrier() call từ valid RFID
│   ├── Action: servo.write(90), start timer
│   └── Duration: 2 seconds fixed
├── OPENING → WAITING_VEHICLE:
│   ├── Trigger: 2 seconds elapsed
│   ├── Action: Reset detection counters
│   └── Start: Vehicle detection monitoring
├── WAITING_VEHICLE → VEHICLE_PRESENT:
│   ├── Trigger: 3 consecutive detections (ULTRA_STABLE_COUNT)
│   ├── Validation: Distance <= ULTRA_THRESHOLD_CM (10cm)
│   └── Timeout: 30 seconds → TIMEOUT_CLOSING
├── VEHICLE_PRESENT → CLOSING:
│   ├── Trigger: 3 consecutive "no vehicle" readings
│   ├── Safety: Final 200ms delay + re-check
│   └── Action: servo.write(0), start close timer
└── CLOSING/TIMEOUT_CLOSING → IDLE:
    ├── Duration: 2 seconds servo movement
    ├── Action: Reset all counters và timers
    └── Ready: Sẵn sàng cho cycle tiếp theo
```

**🛡️ Safety & Noise Filtering:**
```cpp
Vehicle Detection Algorithm:
├── Noise Filtering:
│   ├── ULTRA_STABLE_COUNT = 3 (consecutive readings required)
│   ├── presentCount++ khi distance <= 10cm
│   ├── absentCount++ khi distance > 10cm hoặc timeout
│   └── State change chỉ sau 3 stable readings
├── Safety Mechanisms:
│   ├── Final safety check: 200ms delay trước closing
│   ├── Emergency timeout: SERVO_MAX_OPEN_MS (30 seconds)
│   ├── Force override: openBarrier() có thể interrupt CLOSING
│   └── Distance validation: Reject readings > reasonable range
└── Error Recovery:
    ├── Timeout handling trong mọi states
    ├── State reset khi gặp lỗi sensor
    └── Graceful degradation khi ultrasonic fail
```

**⚡ Non-Blocking Implementation:**
```cpp
Performance Features:
├── millis() based timing: Không dùng delay() blocking calls
├── Independent barriers: IN và OUT hoạt động song song
├── State persistence: Maintain state qua multiple loop() cycles  
├── Minimal overhead: Chỉ check timing khi cần thiết
└── Responsive control: 10ms main loop delay cho real-time response
```

### 🔧 **ESP32 Parking Sensors**

📁 **File: `hardware/esp32_sensors/esp32_main.ino`**

**Chức năng chính:** Hệ thống quản lý 6 cảm biến siêu âm HY-SRF05 với power switching thông minh để phát hiện xe trong bãi đỗ

**🏗️ ESP32 Sensors Architecture dựa trên code thực tế:**

#### **Power Switching System với 74HC595 + MOSFET**
```cpp
Kiến trúc Power Management:
├── 74HC595 Shift Register:
│   ├── DS (Pin 23): Serial data input  
│   ├── SH_CP (Pin 18): Shift register clock
│   └── ST_CP (Pin 5): Storage register latch
├── MOSFET Control Array (Q1-Q6):
│   ├── Q1 → MOSFET → VCC cho HY-SRF05 #1
│   ├── Q2 → MOSFET → VCC cho HY-SRF05 #2
│   ├── Q3 → MOSFET → VCC cho HY-SRF05 #3
│   ├── Q4 → MOSFET → VCC cho HY-SRF05 #4
│   ├── Q5 → MOSFET → VCC cho HY-SRF05 #5
│   └── Q6 → MOSFET → VCC cho HY-SRF05 #6
└── Power Switching Logic:
    ├── Chỉ 1 sensor có VCC tại 1 thời điểm
    ├── Bit patterns cho từng MOSFET (0b00000010 → 0b01000000)
    ├── 200ms startup delay sau khi bật VCC
    └── Tự động tắt sau khi đọc (tiết kiệm điện)
```

#### **Sensor Reading với Power Cycling**
```cpp
Quy trình đọc sensor:
1. tatTatCaNguon() → Tắt tất cả MOSFET
2. batNguonSensor(i) → Bật VCC cho sensor thứ i
3. delay(200) → Đợi sensor khởi động  
4. docKhoangCachCM(i) → Đọc TRIG/ECHO
5. tatTatCaNguon() → Tắt VCC ngay lập tức
6. Lặp lại cho sensor tiếp theo

Ultrasonic Processing:
├── TRIG pulse: 10μs HIGH signal
├── ECHO measurement: pulseIn() với 40ms timeout
├── Distance calculation: time / 29.1 / 2 (cm)
└── Occupancy logic: ≤15cm = có xe (1), >15cm = trống (0)
```

#### **Network & API Architecture**
```cpp  
WiFi Configuration:
├── SSID: "UNO-R4-AP" (kết nối vào UNO R4 WiFi)
├── Static IP: 192.168.4.5
├── Gateway: 192.168.4.2 (UNO R4 WiFi)
└── Auto-reconnection: 30s check interval, 10s timeout

HTTP Server Endpoints:
├── GET /data:
│   ├── Trả về current sensor data (format tương thích backend cũ)
│   ├── JSON: {"success": true, "data": [0,1,0,1,0,0], "totalSensors": 6}
│   └── CORS enabled cho cross-origin requests
├── POST /detect:
│   ├── Trigger đọc lại tất cả sensors
│   ├── Reset currentDistances array
│   └── Trả về data mới sau khi scan
└── OPTIONS /*: CORS preflight handling
```

#### **Pull Model Data Flow**
```cpp
Backend Polling Architecture:
├── ESP32 HTTP Server (Port 80):
│   ├── Chỉ phục vụ requests, không push data
│   ├── currentDistances[6] array lưu trữ giá trị cuối
│   └── Chỉ đọc sensors khi có request (/detect)
├── Backend Poll Schedule:
│   ├── Tự động poll mỗi 30 phút
│   ├── Manual trigger qua admin panel
│   └── Timeout 10s cho mỗi HTTP request
└── Data Processing:
    ├── Raw distance → Binary occupancy (0/1)
    ├── Error handling: -1 distance → 0 occupancy  
    └── WiFi status bonus info (RSSI, connection state)
```

**🏗️ Arduino UNO R4 WiFi Architecture dựa trên code thực tế:**

**📡 Hardware Configuration:**
```cpp
Component Setup:
├── Dual RFID RC522:
│   ├── IN Reader: SS=10, RST=9 (entrance control)
│   └── OUT Reader: SS=7, RST=8 (exit control)
├── Dual Servo Motors:
│   ├── Servo IN: Pin 5 (0°=closed, 90°=open)
│   └── Servo OUT: Pin 6 (0°=closed, 90°=open)
├── Dual Ultrasonic Sensors:
│   ├── IN Sensor: TRIG=3, ECHO=4 (vehicle detection)
│   └── OUT Sensor: TRIG=2, ECHO=A0 (vehicle detection)
└── WiFi AP Configuration:
    ├── SSID: "UNO-R4-AP", Password: "12345678"
    ├── Static IP: 192.168.4.2 (Gateway + AP)
    └── Web Server: Port 80 (health check endpoint)
```

**🔄 Non-Blocking State Machine System:**
```cpp
enum BarrierState {
  IDLE,               // Barrier closed, ready for command
  OPENING,            // Servo opening (2 seconds)
  WAITING_VEHICLE,    // Open, waiting for vehicle detection
  VEHICLE_PRESENT,    // Vehicle detected, waiting to pass
  CLOSING,            // Servo closing (2 seconds)  
  TIMEOUT_CLOSING     // Emergency closure due to timeout
}

struct BarrierControl {
  BarrierState state;
  unsigned long stateStartTime;
  int presentCount, absentCount;    // Noise filtering counters
  bool vehicleDetected;
  Servo* servo;
  int trigPin, echoPin;
  String name;                      // "IN" or "OUT"
}
```

**⚡ Main Loop - Parallel Processing:**
```cpp
void loop() {
  // Parallel barrier state machine updates
  updateBarrier(barrierIn);   // Non-blocking IN barrier control
  updateBarrier(barrierOut);  // Non-blocking OUT barrier control
  
  // Independent RFID readers với separate cooldowns
  static lastRfidTimeIN, lastRfidTimeOUT;
  static lastUID_IN, lastUID_OUT;
  
  // IN Reader: 100ms intervals, 3s UID memory
  if (millis() - lastRfidTimeIN > 100ms) {
    String uidIn = readRFID(rfidIn, "IN");
    if (uidIn != "" && uidIn != lastUID_IN) {
      sendRFIDToServer(uidIn, "IN");  // HTTP POST to backend
    }
  }
  
  // OUT Reader: Independent processing 
  if (millis() - lastRfidTimeOUT > 100ms) {
    String uidOut = readRFID(rfidOut, "OUT");
    if (uidOut != "" && uidOut != lastUID_OUT) {
      sendRFIDToServer(uidOut, "OUT");  // HTTP POST to backend
    }
  }
  
  // Web server health check handling
  handleWebServerRequests();  // Port 80 status endpoint
}
```

**🚀 State Machine Logic - updateBarrier():**
```cpp
State Transitions:
├── IDLE: Wait for openBarrier() call from valid RFID
├── OPENING: 2-second servo movement, then → WAITING_VEHICLE
├── WAITING_VEHICLE:
│   ├── Vehicle detected (3 stable readings) → VEHICLE_PRESENT
│   └── Timeout (30s) → TIMEOUT_CLOSING
├── VEHICLE_PRESENT:
│   ├── Vehicle gone (3 stable readings + safety check) → CLOSING
│   └── Emergency timeout → TIMEOUT_CLOSING
└── CLOSING/TIMEOUT_CLOSING: 2-second servo close, then → IDLE
```

**Safety Features:**
- **Noise Filtering**: 3 consecutive readings cho stable detection (ULTRA_STABLE_COUNT)
- **Final Safety Check**: Extra 200ms delay + re-scan trước khi đóng
- **Emergency Timeout**: 30-second max open time (SERVO_MAX_OPEN_MS)  
- **Force Commands**: openBarrier() có thể interrupt CLOSING state

**🌐 Network & API Integration:**
```cpp
sendRFIDToServer(uid, direction):
├── HTTP POST to 192.168.4.3:5000/api/cards/scan
├── JSON Payload: {"card_id": uid, "timestamp": ISO, "direction": "IN"/"OUT"}
├── Response Processing:
│   ├── "success": true → openBarrier(appropriate barrier)
│   ├── "success": false → Log error, no action
│   └── Network error → Offline mode (reject all)
└── Timeout: 1 second để avoid blocking
```

**Response Logic dựa trên Backend API:**
- **Valid Entry/Exit**: Open corresponding barrier (IN vs OUT)
- **Invalid State**: Log specific error (already inside, already outside, unknown card)
- **Server Errors**: Log 500 errors, offline mode
- **Direction-Based Control**: RFID reader location determines barrier selection

**📊 Performance Optimizations:**
- **Non-blocking Design**: State machines thay vì delay() blocking calls
- **Independent Timers**: Separate cooldowns cho dual RFID readers
- **Minimal Loop Delay**: 10ms main loop untuk responsive system
- **Optimized HTTP**: 1s timeout thay vì 3s để reduce latency
- **Memory Management**: String cleanup và efficient buffer usage

**🔧 Configuration Constants:**
```cpp
System Tuning Parameters:
├── ULTRA_THRESHOLD_CM = 10        // Vehicle detection distance  
├── ULTRA_STABLE_COUNT = 3         // Noise filtering iterations
├── SERVO_MAX_OPEN_MS = 30000      // Safety timeout (30 seconds)
├── RFID_COOLDOWN_MS = 200         // Reader debounce interval
└── Web Server Port = 80           // Health check endpoint
```

#### **Power Management System**

**74HC595 Shift Register Control:**
- **Q1-Q6 outputs**: Điều khiển MOSFET gates
- **Sequential activation**: Chỉ 1 sensor active tại 1 thời điểm
- **Power efficiency**: Tiết kiệm điện và giảm EMI interference

**⚡ Power Management Implementation dựa trên esp32_main.ino:**

**🔧 74HC595 + MOSFET Control System:**
```cpp
Hardware Power Switching:
├── 74HC595 Shift Register Control:
│   ├── DS Pin 23: Serial data input
│   ├── SH_CP Pin 18: Shift register clock  
│   ├── ST_CP Pin 5: Storage register latch
│   └── 8-bit output: Q1-Q6 điều khiển MOSFET gates
├── MOSFET Array (6 channels):
│   ├── Q1 (0b00000010) → MOSFET → VCC cho HY-SRF05 #1
│   ├── Q2 (0b00000100) → MOSFET → VCC cho HY-SRF05 #2
│   ├── Q3 (0b00001000) → MOSFET → VCC cho HY-SRF05 #3
│   ├── Q4 (0b00010000) → MOSFET → VCC cho HY-SRF05 #4
│   ├── Q5 (0b00100000) → MOSFET → VCC cho HY-SRF05 #5
│   └── Q6 (0b01000000) → MOSFET → VCC cho HY-SRF05 #6
└── Sensor Array: 6x HY-SRF05 chia sẻ TRIG/ECHO pins với ESP32
```

**🔄 Power Cycling Algorithm:**
```cpp
Smart Power Management:
├── tatTatCaNguon():
│   ├── trangThai = 0b00000000 (All MOSFETs OFF)
│   ├── shiftOut() để update 74HC595
│   └── digitalWrite(chanLatch, HIGH) để apply changes
├── batNguonSensor(sensorNumber):
│   ├── trangThai = qPatterns[sensorNumber-1] (1 MOSFET ON)
│   ├── capNhat595() để activate specific MOSFET
│   └── Chỉ sensor được chọn có VCC, others OFF
└── docTatCaCamBien():
    ├── FOR each sensor 1→6:
    │   ├── tatTatCaNguon() → Tắt tất cả
    │   ├── delay(100) → Đợi sensors tắt hoàn toàn
    │   ├── batNguonSensor(i) → Bật VCC cho sensor i
    │   ├── docKhoangCachCM(i) → Đọc với 200ms startup delay
    │   └── tatTatCaNguon() → Tắt ngay sau đọc xong
    └── Result: Only 1 sensor powered at any moment
```

**📊 Sensor Reading với Power Switching:**
```cpp
docKhoangCachCM() Function:
├── Pre-conditions: Sensor đã có VCC (MOSFET ON)
├── Startup delay: 200ms cho HY-SRF05 khởi động ổn định
├── Pin configuration:
│   ├── pinMode(sensorPin, OUTPUT) → Chuẩn bị TRIG
│   ├── 10μs TRIG pulse generation
│   └── pinMode(sensorPin, INPUT) → Chuyển sang ECHO mode
├── ECHO measurement:
│   ├── pulseIn(sensorPin, HIGH, 40000) → 40ms timeout
│   ├── Distance calculation: time / 29.1 / 2 (cm)
│   └── Error handling: timeout → return -1
└── Occupancy logic: ≤15cm = occupied (1), >15cm = empty (0), -1 = error (0)
```

**⚡ Power Efficiency Benefits:**
```cpp
Energy Saving Features:
├── Reduced Power Consumption:
│   ├── 83% power saving (1/6 sensors active vs all 6)
│   ├── Lower heat generation từ sensors
│   └── Extended system runtime on battery power
├── EMI Noise Reduction:
│   ├── No crosstalk giữa multiple sensors
│   ├── Cleaner measurements do isolated operation
│   └── Reduced electromagnetic interference
├── System Reliability:
│   ├── Individual sensor failures không affect others
│   ├── Power cycling helps reset stuck sensors
│   └── Controlled startup sequence cho stable operation
└── Scalability: Easy expansion tới 8 sensors (74HC595 limit)
```

#### **HTTP Server Endpoints**

**🌐 Pull Model API Server dựa trên esp32_main.ino:**

**📡 ESP32 HTTP Endpoints Implementation:**
```cpp
Web Server Architecture (Port 80):
├── GET /data → handleGetData():
│   ├── Return current sensor states (0/1) cho 6 slots
│   ├── Format: {"success": true, "data": [0,1,0,1,0,0], "totalSensors": 6}
│   ├── Live WiFi info: connection status + RSSI
│   └── Compatible với backend polling expectations
├── POST /detect → handleDetect():
│   ├── Trigger docTatCaCamBien() → Full sensor re-scan
│   ├── Update currentDistances[6] array với fresh readings
│   ├── Return updated data array sau scanning
│   └── Manual refresh cho admin panel
├── OPTIONS /* → handleCORS():
│   ├── Preflight CORS handling
│   ├── Access-Control-Allow-Origin: *
│   ├── Methods: GET, POST, OPTIONS
│   └── Headers: Content-Type supported
└── 404 Handler → handleNotFound(): Standard error response
```

**🔄 Pull Model Data Flow:**
```cpp
Backend Polling Architecture:
├── ESP32 Server Role:
│   ├── Passive server: Chỉ response khi được request
│   ├── No push notifications hoặc webhooks  
│   ├── currentDistances[6] cache cho fast response
│   └── On-demand sensor reading với /detect endpoint
├── Backend Client Behavior:
│   ├── Scheduled polling: Mỗi 30 phút tự động
│   ├── Manual triggers: Admin panel "Refresh Slots"
│   ├── Timeout handling: 10s limit cho HTTP requests
│   └── Fallback logic: Continue với cached data nếu ESP32 offline
└── Data Processing Pipeline:
    ├── Raw distances → Binary occupancy (≤15cm = occupied)
    ├── Error handling: -1 distances mapped to 0 (empty)
    └── JSON format compatible với existing backend code
```

**🛡️ CORS & Security Features:**
```cpp
Cross-Origin Support:
├── Access-Control-Allow-Origin: "*" (open access)
├── Access-Control-Allow-Methods: "GET, POST, OPTIONS"
├── Access-Control-Allow-Headers: "Content-Type"
├── Preflight handling cho complex requests
└── No authentication required (internal IoT network)

Network Resilience:
├── WiFi reconnection: Auto-detect disconnections mỗi 30s
├── Static IP maintenance: Preserve 192.168.4.5 assignment
├── Connection recovery: Retry logic với timeout handling
└── Graceful degradation: Local operation khi network issues
```

---

## 🔄 Luồng Hoạt Động Tổng Thể

### 🔍 **Chi Tiết Từng Bước - Luồng Hoạt Động Complete**

#### **Bước 1: Hardware Detection & Data Transmission**

**Arduino UNO R4 WiFi - RFID Processing:**

**🔍 Dual RFID Detection Flow dựa trên uno_r4_wifi.ino:**
```cpp
RFID Processing Pipeline:
├── Dual Reader Setup:
│   ├── rfidIn (SS=10, RST=9): Entrance detection
│   ├── rfidOut (SS=7, RST=8): Exit detection  
│   └── Shared SPI bus với independent SS control
├── Reading Cycle (mỗi 100ms):
│   ├── Check rfidIn.PICC_IsNewCardPresent()
│   ├── readRFID(rfidIn, "IN") → Extract UID string
│   ├── Compare với lastUID_IN cache (3s cooldown)
│   └── Parallel processing cho rfidOut reader
├── UID Processing:
│   ├── Convert MFRC522::Uid to hex string
│   ├── Normalize format: uppercase, consistent length
│   ├── Cache management: 3-second duplicate prevention
│   └── Direction tagging: "IN" vs "OUT" for backend
└── HTTP Communication:
    ├── sendRFIDToServer(uid, direction)
    ├── POST to 192.168.4.3:5000/api/cards/scan
    ├── JSON payload: {card_id, timestamp, direction}
    └── Parse response → openBarrier() if success=true
```

**⚡ Smart Detection Logic:**
```cpp
Anti-Duplicate System:
├── UID Memory: lastUID_IN, lastUID_OUT caching
├── Time-based Cooldown: 3 seconds per reader
├── Independent Tracking: IN và OUT readers isolated
└── Reset Logic: Cooldown expires → accept same card again

Direction-Aware Processing:  
├── IN Reader Detection:
│   ├── Expected: Car entering parking (status 0→1)
│   ├── HTTP payload: {"card_id": "ABC123", "direction": "IN"}
│   ├── Backend validation: Prevent double entry
│   └── Barrier control: Open IN barrier if valid
└── OUT Reader Detection:
    ├── Expected: Car exiting parking (status 1→0)  
    ├── HTTP payload: {"card_id": "ABC123", "direction": "OUT"}
    ├── Backend validation: Prevent invalid exit
    └── Barrier control: Open OUT barrier if valid
```

**ESP32 - Sensor Data Collection:**

**📊 Power-Switched Sensor Scanning dựa trên esp32_main.ino:**
```cpp
docTatCaCamBien() Implementation:
├── Sequential Sensor Processing (1→6):
│   ├── tatTatCaNguon() → Turn OFF all MOSFETs
│   ├── delay(100) → Wait for complete power down
│   ├── batNguonSensor(s) → Power ON sensor #s only
│   ├── Serial feedback: "VCC ON →" status logging
│   └── docKhoangCachCM(s) → Read với 200ms startup delay
├── Data Storage:
│   ├── currentDistances[s-1] = distance_cm
│   ├── Error handling: -1 for timeout/error readings
│   └── Real-time logging: Distance values in cm
├── Power Management:
│   ├── tatTatCaNguon() → Turn OFF sensor after reading
│   ├── delay(50) → Inter-sensor delay for stability
│   └── Final cleanup: Ensure all sensors powered down
└── Completion Status:
    ├── Console log: "Power switching scan completed"
    └── Confirmation: "Only 1 sensor powered at a time!"
```

**🔄 HTTP Pull Model Data Flow:**
```cpp
Backend Integration Architecture:
├── Data Endpoint (/data):
│   ├── Return cached currentDistances[] values
│   ├── No real-time scanning → Use last readings
│   ├── Convert distance to occupancy: ≤15cm = 1, >15cm = 0
│   └── Include WiFi status bonus info (RSSI, connection)
├── Detect Endpoint (/detect):
│   ├── Trigger docTatCaCamBien() → Fresh scan all 6
│   ├── Update currentDistances[] with new readings  
│   ├── Return updated occupancy data array
│   └── Manual refresh capability for admin panel
└── Response Format (Compatible với backend cũ):
    {
      "success": true,
      "data": [0,1,0,1,0,0],      // Binary occupancy
      "totalSensors": 6,
      "soIC": 1,                  // Legacy field
      "wifi_connected": true,
      "wifi_rssi": -45
    }
```

**⚡ Real-time Processing Logic:**
```cpp
Distance to Occupancy Conversion:
├── Raw Reading Processing:
│   ├── docKhoangCachCM() returns: distance_cm or -1 (error)
│   ├── Timeout handling: 40ms pulseIn() limit
│   └── Error mapping: -1 → 0 (treat as empty slot)
├── Occupancy Detection Logic:
│   ├── currentDistances[i] ≤ 15 → dataArray.add(1) // Vehicle present
│   ├── currentDistances[i] > 15 → dataArray.add(0)  // Empty slot
│   └── currentDistances[i] == -1 → dataArray.add(0) // Error = empty
└── Data Caching Strategy:
    ├── currentDistances[6] global array for storage
    ├── /data endpoint serves cached values (fast response)
    ├── /detect endpoint triggers fresh scanning (slow but accurate)
    └── No automatic refresh → Backend controls polling schedule
```

#### **Bước 2: Backend Processing**

**Card Scan API Endpoint:**

**🔍 POST /api/cards/scan Implementation dựa trên cards.py:**
```python
Hardware Integration Endpoint:
├── Kiểm tra dữ liệu đầu vào:
│   ├── Content-Type: application/json bắt buộc
│   ├── Trường bắt buộc: card_id (RFID UID)
│   ├── Trường tùy chọn: direction ("IN"/"OUT"), timestamp
│   └── ValidationHelper.validate_card_id() kiểm tra định dạng
├── Xử lý theo hướng:
│   ├── Xử lý đầu đọc vào (IN):
│   │   ├── Mong đợi: Xe vào bãi (status 0→1)
│   │   ├── Kiểm tra: Từ chối nếu đã đỗ (status=1)
│   │   └── Hành động: "entry" với new_status=1
│   ├── Xử lý đầu đọc ra (OUT):
│   │   ├── Mong đợi: Xe rời bãi (status 1→0)  
│   │   ├── Kiểm tra: Từ chối nếu đã ở ngoài (status=0)
│   │   └── Hành động: "exit" với new_status=0
│   └── Logic dự phòng: Chuyển đổi status nếu thiếu direction
├── Xử lý trạng thái thẻ:
│   ├── Thẻ đã biết: card_service.get_card() tra cứu
│   ├── Cập nhật trạng thái: card_service.update_card_status()
│   ├── Ghi nhật ký kiểm toán: Tự động ghi entry/exit/scan
│   └── Phản hồi barrier: success=true kích hoạt mở barrier
└── Xử lý thẻ chưa biết:
    ├── Tự động thêm: card_service.add_unknown_card()
    ├── Ghi nhật ký: log_service.log_unknown_card()
    ├── Phản hồi: 403 Forbidden với hành động reject
    └── Hành động hardware: Không mở barrier
```

**📊 Định dạng Response cho Hardware Control:**
```python
Success Response (thẻ đã biết):
{
  "success": true,
  "card": {card_object},
  "action": "entry|exit",           // Loại hành động
  "direction": "IN|OUT",            // Hướng đầu đọc
  "message": "Card entry processed",
  "parking_status": "parked|available",
  "timestamp": "ISO_TIMESTAMP"
}

Error Response (trạng thái không hợp lệ):
{
  "success": false,
  "error": "Invalid entry|Invalid exit",
  "message": "Xe đã ở trong bãi rồi",
  "action": "reject",               // Hardware không nên mở
  "current_status": "parked|available"
}

Unknown Card Response:
{
  "success": false,
  "error": "Unknown card", 
  "message": "Card not registered in system",
  "action": "reject",
  "card_id": "UNKNOWN123",
  "unknown_card_logged": true
}
```

**Xử lý logic nghiệp vụ:**

**⚙️ Logic nghiệp vụ CardService dựa trên card_service.py:**
```python
Các hoạt động nghiệp vụ cốt lõi:
├── Quản lý vòng đời thẻ:
│   ├── create_card(uid, status=0):
│   │   ├── Kiểm tra trùng lặp: Ngăn chặn UID đã tồn tại
│   │   ├── Tạo đối tượng ParkingCard với giá trị mặc định
│   │   ├── Ghi atomic: Serialize cards_data + file_manager.write_json()
│   │   ├── Tự động ghi log: LogAction.CARD_CREATED với metadata
│   │   └── Trả về: (success, vietnamese_message, card_object)
│   ├── update_card_status(uid, new_status):
│   │   ├── Tải thẻ hiện tại từ storage
│   │   ├── Kiểm tra nghiệp vụ: logic card.update_status()
│   │   ├── Theo dõi thời gian: Tự động set entry_time/exit_time
│   │   ├── Ghi nhật ký kiểm toán: LogAction.CARD_ENTRY/EXIT theo status
│   │   └── Lưu trữ atomic với backup rotation
│   └── delete_card(uid):
│       ├── Kiểm tra tồn tại
│       ├── Xóa khỏi cards_dict
│       ├── Ghi lại toàn bộ file để duy trì tính nhất quán
│       └── Audit trail LogAction.CARD_DELETED
├── Tính toán thống kê:
│   ├── get_statistics() Các chỉ số thời gian thực:
│   │   ├── total_cards: len(cards_dict)
│   │   ├── inside_parking: sum(status == 1)
│   │   ├── outside_parking: total - inside
│   │   └── occupancy_rate: (inside/total * 100) if total > 0
│   └── Hiệu suất: Tính toán single-pass cho dashboard
└── Quản lý thẻ chưa biết:
    ├── add_unknown_card(uid, metadata):
    │   ├── Chuẩn hóa UID: uid.upper().strip()
    │   ├── Ngăn chặn trùng lặp: Kiểm tra unknown_cards hiện tại
    │   ├── Làm giàu metadata: timestamp + custom fields
    │   ├── Tự động ghi log: LogAction.UNKNOWN_CARD
    │   └── Lưu trữ bền vững: unknown_cards.json
    └── Tích hợp: Được gọi từ /scan endpoint cho thẻ chưa đăng ký
```

**🔄 Tích hợp Service & Xử lý lỗi:**
```python
Quản lý phụ thuộc:
├── Mẫu Lazy Loading:
│   ├── @property backup_service → BackupService()
│   ├── @property log_service → CardLogService()
│   └── Tránh circular imports với dynamic resolution
├── Tích hợp File Manager:
│   ├── read_json(CARDS_FILE, default={}) → Tải an toàn
│   ├── write_json(file, data, max_backups=5) → Ghi atomic
│   ├── Backup rotation → Ngăn đầy ổ cứng
│   └── Khôi phục lỗi từ backups nếu file chính bị hỏng
├── Xử lý lỗi toàn diện:
│   ├── Try-catch wrapper cho tất cả methods
│   ├── Mẫu trả về tuple: (success: bool, message: str, data: Optional)
│   ├── Thông báo người dùng tiếng Việt vs log messages tiếng Anh
│   ├── Degradation nhẹ nhàng: Trả về {} thay vì crash
│   └── Cô lập logging: Lỗi service không làm hỏng operations chính
└── Tối ưu hóa hiệu suất:
    ├── Xử lý in-memory: Mẫu Load → process → save
    ├── Thao tác batch: Single file write cho nhiều thay đổi
    ├── Tra cứu hiệu quả: Lưu trữ thẻ dựa trên Dictionary
    └── I/O tối thiểu: Chỉ ghi khi có thay đổi thực sự
```

**📊 Luồng dữ liệu thời gian thực:**
```python
Pipeline cập nhật trạng thái (Hardware → Backend):
1. Quét RFID → endpoint /api/cards/scan
2. Kiểm tra hướng → logic checking IN/OUT
3. Tra cứu thẻ → card_service.get_card(uid)
4. Chuyển đổi trạng thái → card.update_status(new_status)
5. Quy tắc nghiệp vụ → Ngăn thay đổi trạng thái không hợp lệ
6. Theo dõi thời gian → Tự động set entry_time/exit_time
7. Ghi nhật ký kiểm toán → LogAction.CARD_ENTRY/EXIT
8. Lưu trữ file → Ghi atomic JSON với backups
9. Tạo response → Điều khiển barrier hardware
10. Cập nhật thống kê → Làm mới dashboard thời gian thực
```

#### **Bước 3: Cập nhật Frontend**

**Đồng bộ dữ liệu thời gian thực:**
- Dashboard tự động refresh mỗi 30 giây
- Nút refresh thủ công cho cập nhật tức thì
- Xử lý lỗi và retry logic
- Trạng thái loading và phản hồi người dùng

---

## 🔧 Cập Nhật Real-time & Hiệu Suất

### ⚡ **Hệ Thống Cập Nhật**

**Triển khai hiện tại**: Phương pháp HTTP polling
- **Tự động refresh**: Khoảng thời gian 30 giây cho dashboard
- **Refresh thủ công**: Nút cập nhật tức thì
- **Không WebSocket**: Các cuộc gọi HTTP API đơn giản
- **Polling endpoints**: `/api/cards/statistics` và `/api/cards/logs`

**Lợi ích**: Đơn giản, đáng tin cậy, thân thiện với trình duyệt, có thể mở rộng mà không cần kết nối liên tục

### 🚀 **Tính năng hiệu suất**

- **Thao tác file atomic**: Ngăn chặn hỏng dữ liệu trong quá trình ghi JSON
- **Background tasks**: Hệ thống backup tự động qua threading
- **Kiểm tra đầu vào**: Validation toàn diện trên tất cả endpoints
- **Xử lý lỗi**: Xử lý lỗi nhiều lớp với ghi log chi tiết
- **Cấu hình CORS**: Chia sẻ tài nguyên cross-origin an toàn

---

## 🔒 Bảo Mật & Xử Lý Lỗi

### 🔒 **Các Biện Pháp Bảo Mật**
- Làm sạch và kiểm tra đầu vào cho tất cả API endpoints
- Cấu hình CORS để bảo mật giao tiếp frontend-backend
- Xử lý lỗi toàn diện với HTTP status codes phù hợp
- Ghi nhật ký kiểm toán cho tất cả thao tác thẻ và sự kiện hệ thống

### ⚠️ **Xử Lý Lỗi**
- Frontend error boundaries và cơ chế fallback
- Backend exception handling với structured error responses
- Hardware retry logic cho các thao tác mạng
- Giảm hiệu suất nhẹ nhàng khi các thành phần offline

---

## 🛠️ Công Cụ Phát Triển & Cải Tiến Tương Lai

### 🛠️ **Thiết Lập Môi Trường Phát Triển**
- **Frontend**: React TypeScript với development server tự động tải lại
- **Backend**: Python Flask với thiết lập môi trường ảo
- **Hardware**: Arduino IDE để lập trình vi điều khiển
- **Kiểm tra API**: Lệnh cURL để xác thực endpoint

### 🔮 **Các Cải Tiến Tiềm Năng**
- Chuyển đổi database (PostgreSQL/MySQL) để cải thiện hiệu suất
- JWT authentication để tăng cường bảo mật
- Thông báo email/SMS cho các sự kiện hệ thống
- Phát triển ứng dụng mobile với React Native
- Phân tích nâng cao và tính năng báo cáo

---

## 🎓 Tóm Tắt Dự Án

### 📝 **Thành Tựu Kỹ Thuật**
1. **Kiến trúc Full-stack**: React TypeScript frontend + Python Flask backend
2. **Tích hợp IoT**: Arduino UNO R4 WiFi + ESP32 với cảm biến RFID/siêu âm
3. **Thiết kế RESTful API**: HTTP methods phù hợp với xử lý lỗi toàn diện
4. **Giao tiếp Hardware**: Trao đổi dữ liệu cảm biến qua HTTP
5. **Quản lý dữ liệu**: Lưu trữ JSON với tính năng backup/restore
6. **Tính năng Real-time**: Cập nhật dashboard theo polling

### 💡 **Kết Quả Học Tập**
- Thiết kế và triển khai kiến trúc phân lớp
- Tích hợp API giữa frontend và backend
- Lập trình IoT và tích hợp cảm biến
- Thực hành tốt về xử lý lỗi và ghi log
- Phối hợp dự án đa vi điều khiển
- Quản lý toàn bộ chu kỳ phát triển

---