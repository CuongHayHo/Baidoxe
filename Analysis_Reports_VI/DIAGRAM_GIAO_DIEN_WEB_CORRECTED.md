# 3.4 Giao diện Web - CORRECTED VERSION

## Tổng quan:
Giao diện Web cung cấp cho nhân viên soát vé một dashboard thực tế để đối dòng thông tin xe và quản lý các thông tin xe. Giao diện kết nối trực tiếp với Backend Server (Python Flask) thông qua HTTP API, sử dụng Polling - Backend tự động polls ESP32 mỗi 30 phút để lấy dữ liệu cảm biến.

---

## 3.4.1 Kiến trúc Giao diện (Architecture)

### Frontend Stack:

| Thành phần | Công nghệ | Mục đích |
|-----------|-----------|---------|
| **Frontend Framework** | HTML5 + CSS3 + React 18.2.0 + TypeScript | Giao diện người dùng |
| **API Client** | Axios 1.6.0 | Gửi request tới Backend |
| **Real-time Update** | Polling (30 giây lấy dữ liệu mới) | Cập nhật trạng thái động |
| **Responsive Design** | CSS tùy chỉnh | Tương thích mobile/tablet |
| **Routing** | React Router DOM v7.9.4 | Điều hướng giữa các trang |

---

## 3.4.2 Các Module Chính của Giao diện

### 1. Dashboard - Hiển thị Trạng thái Bãi Xe
**Chức năng:**
- Tổng quan nhanh hệ thống
- Giao diện chính: các chỉ số **Tổng số thế. Xe trong bãi, Xe ngoài bãi, Tỷ lệ sử dụng (%), Tính tình thái "Trống → Đầy", Hoạt động gần đây.
- Dữ liệu vào: thông báo từ backend (đếm thế, trạng thái 0/1, logs gần nhất).
- Dữ liệu ra: UI: liệu KPI, biểu đồ thanh, danh sách chi kiến mới.
- Tấn suất cập nhật: thì công (Lấy mới) hoặc chọ cáu hình.

### 2. Danh sách Thẻ (Card Management)
**Chức năng:**
- Xem tất cả thẻ xe và thông tin liên quan (ID thẻ, chủ sở hữu, trạng thái, ngày đăng ký).
- Thêm/Xóa/Sửa thẻ.
- Tìm kiếm và lọc theo trạng thái.

### 3. Quản lý Bãi xe (Parking Slots Management)
**Chức năng:**
- Xem trạng thái từng vị trí bãi (occupied/empty).
- Bản đồ hoặc danh sách bãi.
- Cập nhật thực tế từ cảm biến ESP32.

### 4. Xem Logs (Log Viewer)
**Chức năng:**
- Xem lịch sử quét thẻ, vào/ra, lỗi hệ thống.
- Lọc theo ngày, giờ, loại, ID thẻ.
- Export dữ liệu (nếu cần).

### 5. Bảng Điều Khiển Quản Trị (Admin Panel)
**Chức năng:**
- Quản lý tài khoản nhân viên, phân quyền.
- Cấu hình hệ thống, backup/restore dữ liệu.
- Thống kê, báo cáo chi tiết.

---

## 3.4.3 Luồng Dữ liệu

```
Frontend (React) 
    ↓ (HTTP Request + Axios)
Backend Server (Flask) 
    ↓ (Query/Command)
Database (SQLite)
    ↓ (Sensor Data)
ESP32 + UNO R4 (Polling 30 phút)
```

---

## 3.4.4 Quy trình Cập nhật Dữ liệu

- **Polling**: Frontend gửi request mỗi 30 giây (configurable) để lấy dữ liệu mới từ Backend.
- **Query chậm**: Cần tối ưu dùng view/cached table để tránh query quá lâu.
- **DB trống**: Trả toàn 0.

---

## Ghi chú:
- ✅ **Đã sửa**: Thay thế "Bootstrap/Tailwind CSS" → "CSS tùy chỉnh"
- ✅ **Đã sửa**: Loại bỏ "Chart.js / Plotly" vì dự án không sử dụng
- ✅ **Thêm chi tiết**: React Router DOM version để chính xác
- ✅ **Rõ ràng hóa**: Polling mechanism (30 giây)
