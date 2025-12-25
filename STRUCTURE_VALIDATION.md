# 📊 Kiểm Tra Cấu Trúc JSON vs Database Models

## 1. CARDS.JSON vs Card Model

### ✅ Trường Có Trong JSON:
| Trường | Kiểu | Vị trí | Ghi chú |
|--------|------|--------|---------|
| `uid` | string | Key of object | VD: "TEST002", "A1B3C2" |
| `name` | string | ✅ Có | VD: "cuonghayhyy", "Cuong" |
| `status` | number | ✅ Có | 0 = outside, 1 = inside |
| `created_at` | string (ISO) | ✅ Có | VD: "2025-12-25T07:43:12.069037+00:00" |
| `entry_time` | string (ISO) | ✅ Có (optional) | Chỉ có khi xe vào bãi |
| `exit_time` | string (ISO) | ✅ Có (optional) | Chỉ có khi xe ra khỏi bãi |
| `parking_duration` | object | ✅ Có (optional) | Chứa: total_seconds, hours, minutes, display |

### ✅ Card Model Fields:
```python
self.uid = uid                           # ✅ Có
self.status = status                     # ✅ Có
self.entry_time = entry_time             # ✅ Có
self.exit_time = exit_time               # ✅ Có
self.created_at = created_at             # ✅ Có
self.name = name                         # ✅ Có
self.parking_duration = None             # ✅ Có (tính toán)
```

### ✅ KẾT LUẬN: **ĐÚNG** - Cấu trúc cards.json hoàn toàn khớp với Card model

---

## 2. CARD_LOGS.JSON vs CardLog Model

### ✅ Trường Có Trong JSON:
```json
{
  "logs": [
    {
      "id": "57b588ae-bc4d-4a0a-8166-1fdc0434e334",      // ✅ UUID
      "timestamp": "2025-10-06T15:18:15.914682+00:00",    // ✅ ISO format
      "card_id": "TEST123",                                // ✅ Card UID
      "action": "unknown",                                 // ✅ Action type
      "details": {                                         // ✅ Extra info
        "source": "esp32",
        "local_time": "2025-10-06 22:18:15"
      },
      "metadata": {}                                       // ✅ Meta info
    }
  ]
}
```

### ❌ CardLog Model Fields:
```python
self.card_number = card_number           # ❌ JSON dùng "card_id"
self.action = action                     # ✅ Có
self.timestamp = timestamp               # ✅ Có
self.location = location                 # ❌ KHÔNG có trong JSON
self.parking_slot = parking_slot         # ❌ KHÔNG có trong JSON
self.duration_minutes = duration_minutes # ❌ KHÔNG có trong JSON
self.calculated_fee = calculated_fee     # ❌ KHÔNG có trong JSON
self.notes = notes                       # ❌ KHÔNG có trong JSON
```

### ⚠️ VẤNĐỀ PHÁT HIỆN:

| Vấn đề | JSON | Model | Độ Severity | Ghi chú |
|--------|------|-------|-------------|---------|
| Tên trường khác | `card_id` | `card_number` | 🔴 CAO | Cần đổi tên trong model |
| Thiếu trường | - | `location` | 🟡 TRUNG | Không sử dụng, có thể xóa |
| Thiếu trường | - | `parking_slot` | 🟡 TRUNG | Không sử dụng, có thể xóa |
| Thiếu trường | - | `duration_minutes` | 🟡 TRUNG | Không sử dụng, có thể xóa |
| Thiếu trường | - | `calculated_fee` | 🟡 TRUNG | Không sử dụng, có thể xóa |
| Thiếu trường | - | `notes` | 🟡 TRUNG | Không sử dụng, có thể xóa |
| Thêm trường | `id` | - | 🟢 THẤP | JSON có UUID, model không |
| Thêm trường | `details` | - | 🟢 THẤP | JSON lưu extra info |
| Thêm trường | `metadata` | - | 🟢 THẤP | JSON lưu metadata |

### ❌ KẾT LUẬN: **SAI** - CardLog model không khớp với cấu trúc JSON hiện tại

---

## 3. ĐỀ XUẤT CẢI TIẾN

### Option A: Cập nhật CardLog Model (Khuyến nghị)
```python
class CardLog:
    """CardLog model - Theo cấu trúc JSON hiện tại"""
    
    def __init__(self, id: str, timestamp: str, card_id: str, action: str, 
                 details: Dict = None, metadata: Dict = None):
        self.id = id                          # UUID
        self.timestamp = timestamp            # ISO format
        self.card_id = card_id               # Card UID (đổi từ card_number)
        self.action = action                 # entry, exit, scan, unknown
        self.details = details or {}         # Extra info (source, local_time, etc)
        self.metadata = metadata or {}       # Metadata
    
    def __repr__(self):
        return f'<CardLog {self.card_id} {self.action} {self.timestamp}>'
```

### Option B: Cập nhật card_logs.json (Không khuyến nghị)
- Thêm các trường: `location`, `parking_slot`, `duration_minutes`, `calculated_fee`, `notes`
- Đổi tên: `card_id` → `card_number`
- **NHƯ CẬU:** Rất nhiều dữ liệu cũ sẽ bị thay đổi

---

## 4. TÓM TẮT

| File | Status | Chi tiết |
|------|--------|---------|
| **cards.json** | ✅ **ĐÚNG** | Khớp hoàn toàn với Card model |
| **card_logs.json** | ❌ **SAI** | Không khớp với CardLog model |

### 🔴 Hành động cần làm:
1. **Cập nhật `backend/models/card_log.py`** để khớp với cấu trúc JSON
2. **Cập nhật tất cả code** sử dụng `CardLog` để dùng các trường mới
3. **Xem xét xóa** các trường không dùng: `location`, `parking_slot`, `duration_minutes`, `calculated_fee`, `notes`

