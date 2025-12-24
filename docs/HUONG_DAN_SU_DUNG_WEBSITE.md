# 🌐 Hướng Dẫn Sử Dụng Website Quản Lý Bãi Đỗ Xe Thông Minh

## 📋 Tổng Quan Hệ Thống

Website **BaiDoXe** là một hệ thống quản lý bãi đỗ xe thông minh sử dụng công nghệ RFID và IoT. Hệ thống giúp tự động hóa việc quản lý xe ra vào bãi đỗ, theo dõi trạng thái xe và thống kê sử dụng bãi xe.

### 🎯 Mục Đích Chính
- **Tự động hóa** việc quản lý xe ra vào bãi đỗ
- **Theo dõi real-time** trạng thái các vị trí đỗ xe
- **Thống kê** và báo cáo sử dụng bãi xe
- **Quản lý thẻ** RFID và thông tin xe
- **Monitoring** hoạt động hệ thống 24/7

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RFID Cards    │───▶│  Arduino UNO R4  │───▶│   Web Server    │
│ (Thẻ xe cá nhân)│    │     WiFi         │    │   (Backend)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
┌─────────────────┐             │               ┌─────────────────┐
│  ESP32 Sensors  │─────────────┘               │  Web Interface  │
│(Cảm biến đỗ xe) │                            │   (Frontend)    │
└─────────────────┘                            └─────────────────┘
```

### 🔧 Thành Phần Phần Cứng
1. **Arduino UNO R4 WiFi**: Đọc thẻ RFID, xử lý logic ra vào
2. **ESP32**: Cảm biến siêu âm để detect xe trong các vị trí
3. **Thẻ RFID**: Mỗi xe có một thẻ duy nhất

### 💻 Thành Phần Phần Mềm
1. **Backend (Python)**: Xử lý logic, lưu dữ liệu, API
2. **Frontend (React)**: Giao diện web để quản lý
3. **Database (JSON)**: Lưu trữ thông tin thẻ và log

---

## 🌟 Các Tính Năng Chính

### 1. 📊 **Dashboard - Trang Chủ**
**Mục đích**: Xem tổng quan hệ thống và thống kê nhanh

**Chức năng**:
- 📈 **Thống kê tổng quan**: Tổng số thẻ, xe trong/ngoài bãi, tỷ lệ sử dụng
- 📊 **Biểu đồ trực quan**: Thanh progress bar hiển thị mức độ đầy của bãi xe
- 🕒 **Hoạt động gần đây**: 10 log hoạt động mới nhất của hệ thống
- ⚡ **Thao tác nhanh**: Backup dữ liệu, sửa lỗi dữ liệu
- 🔄 **Tự động cập nhật**: Làm mới dữ liệu mỗi 30 giây

**Cách sử dụng**:
1. Truy cập trang web → tự động chuyển đến Dashboard
2. Xem thống kê ở 4 thẻ màu: Tổng thẻ, Xe trong bãi, Xe ngoài bãi, Tỷ lệ sử dụng
3. Theo dõi hoạt động gần đây ở phần dưới
4. Sử dụng các nút thao tác nhanh khi cần

### 2. 🎫 **Quản Lý Thẻ**
**Mục đích**: Thêm, xóa, xem danh sách thẻ RFID

**Chức năng**:
- ➕ **Thêm thẻ mới**: Nhập UID thẻ và trạng thái ban đầu
- 📋 **Danh sách thẻ**: Hiển thị tất cả thẻ với thông tin chi tiết
- 🗑️ **Xóa thẻ**: Loại bỏ thẻ khỏi hệ thống
- ⏱️ **Thời gian đỗ**: Tính toán thời gian xe đã đỗ
- 🔄 **Phân trang**: Hiển thị 10 thẻ mỗi trang
- ❓ **Thẻ lạ**: Thông báo thẻ chưa đăng ký

**Cách sử dụng**:
1. **Thêm thẻ mới**:
   - Nhập UID thẻ (ví dụ: A1B2C3D4)
   - Chọn trạng thái: "Ngoài bãi" hoặc "Trong bãi"
   - Nhấn "Thêm thẻ"

2. **Xem danh sách**:
   - Tất cả thẻ hiển thị với UID, trạng thái, thời gian tạo
   - Thẻ trong bãi có màu xanh, ngoài bãi có màu xám
   - Xem thời gian đỗ xe (nếu có)

3. **Xử lý thẻ lạ**:
   - Thông báo màu vàng xuất hiện khi có thẻ lạ
   - Chọn "Thêm vào hệ thống" hoặc "Bỏ qua"

### 3. 🅿️ **Vị Trí Đỗ Xe**
**Mục đích**: Monitor real-time các vị trí đỗ xe từ ESP32

**Chức năng**:
- 🎯 **Sơ đồ bãi xe**: Hiển thị 6 vị trí đỗ xe trực quan
- 🔴 **Trạng thái real-time**: Đỏ = có xe, Xanh = trống
- 📊 **Thống kê**: Số vị trí trống/đã đỗ, tỷ lệ sử dụng
- 🔄 **Reset cảm biến**: Khởi động lại ESP32 sensors
- ⏱️ **Cập nhật tự động**: Dữ liệu mới mỗi 5 giây

**Cách sử dụng**:
1. Xem sơ đồ 6 vị trí đỗ xe (2 hàng x 3 cột)
2. Màu đỏ = có xe đỗ, màu xanh = vị trí trống
3. Nhấn "Reset Cảm Biến" nếu dữ liệu không chính xác
4. Theo dõi thống kê ở phần trên

### 4. 📋 **Nhật Ký Hoạt Động**
**Mục đích**: Xem lịch sử tất cả hoạt động của hệ thống

**Chức năng**:
- 📝 **Log chi tiết**: Mọi hoạt động đều được ghi lại
- 🔍 **Bộ lọc**: Lọc theo loại hoạt động hoặc ID thẻ
- 📄 **Phân trang**: Xem 50 log mỗi trang
- 🕐 **Thời gian**: Hiển thị chính xác thời điểm xảy ra
- 🎯 **Tìm kiếm**: Tìm log theo thẻ cụ thể

**Loại hoạt động được ghi**:
- 🚗➡️ **Vào bãi**: Xe sử dụng thẻ để vào
- 🚗⬅️ **Ra khỏi bãi**: Xe sử dụng thẻ để ra
- 📱 **Quét thẻ**: Hệ thống scan thẻ
- ❓ **Thẻ lạ**: Phát hiện thẻ chưa đăng ký
- ➕ **Tạo thẻ**: Thêm thẻ mới vào hệ thống
- 🗑️ **Xóa thẻ**: Loại bỏ thẻ khỏi hệ thống

**Cách sử dụng**:
1. **Xem tất cả log**: Tự động hiển thị khi vào trang
2. **Lọc theo hành động**:
   - Chọn dropdown "Tất cả hành động"
   - Chọn loại cụ thể (Vào bãi, Ra bãi, etc.)
3. **Lọc theo thẻ**: Nhập ID thẻ vào ô tìm kiếm
4. **Phân trang**: Dùng nút Previous/Next để xem thêm

### 5. ⚙️ **Quản Trị Hệ Thống**
**Mục đích**: Các công cụ quản trị cho admin

**Chức năng**:
- 📊 **Thống kê hệ thống**: Tổng quan toàn bộ hệ thống
- 💾 **Quản lý Backup**: Tạo, xem, khôi phục backup
- 🔧 **Sửa lỗi dữ liệu**: Tự động fix các lỗi thường gặp
- 🗑️ **Xóa log**: Dọn dẹp log cũ
- 📁 **File management**: Quản lý files hệ thống

**Cách sử dụng**:
1. **Tạo Backup**:
   - Nhấn "Tạo Backup Ngay"
   - Hệ thống sẽ lưu snapshot hiện tại

2. **Khôi phục dữ liệu**:
   - Xem danh sách backup files
   - Chọn file muốn khôi phục
   - Xác nhận khôi phục

3. **Sửa lỗi dữ liệu**:
   - Nhấn "Sửa Lỗi Tự Động"
   - Hệ thống kiểm tra và fix lỗi thường gặp

---

## 🔔 Hệ Thống Thông Báo

### 📱 **Toast Notifications**
Hệ thống hiển thị thông báo real-time ở góc màn hình:

- ✅ **Xanh (Success)**: Thao tác thành công
- ❌ **Đỏ (Error)**: Có lỗi xảy ra  
- ⚠️ **Vàng (Warning)**: Cảnh báo quan trọng
- ℹ️ **Xanh dương (Info)**: Thông tin chung

### 🔄 **Real-time Updates**
- **Activity Monitor**: Thông báo khi có hoạt động mới (xe vào/ra)
- **Stats Monitor**: Cảnh báo khi bãi xe gần đầy (>90%) hoặc đầy (100%)
- **Unknown Cards**: Alert khi có thẻ lạ

---

## 🚀 Quy Trình Hoạt Động Thực Tế

### 📝 **Kịch Bản 1: Xe Vào Bãi**
1. **Xe đến cửa vào** → Tài xế đưa thẻ RFID
2. **Arduino đọc thẻ** → Kiểm tra thẻ có trong hệ thống không
3. **Nếu hợp lệ**:
   - Cập nhật trạng thái thẻ: `Ngoài bãi` → `Trong bãi`
   - Ghi log vào hệ thống với thời gian vào
   - Hiển thị thông báo trên web: "Xe vào bãi"
   - Mở cửa cho xe vào
4. **ESP32 cảm biến** → Detect xe đỗ vào vị trí nào
5. **Cập nhật sơ đồ** → Vị trí chuyển màu đỏ trên web

### 📝 **Kịch Bản 2: Xe Ra Bãi**
1. **Xe đến cửa ra** → Tài xế đưa thẻ RFID
2. **Arduino đọc thẻ** → Kiểm tra thẻ có đang trong bãi không
3. **Nếu hợp lệ**:
   - Cập nhật trạng thái: `Trong bãi` → `Ngoài bãi`
   - Tính thời gian đỗ xe (thời gian ra - thời gian vào)
   - Ghi log với thông tin thời gian đỗ
   - Hiển thị: "Xe ra bãi - Thời gian đỗ: X giờ Y phút"
   - Mở cửa cho xe ra
4. **ESP32 detect** → Vị trí đỗ trở thành trống
5. **Cập nhật sơ đồ** → Vị trí chuyển màu xanh

### 📝 **Kịch Bản 3: Thẻ Lạ**
1. **Thẻ không đăng ký** → Arduino không tìm thấy trong database
2. **Ghi log "unknown"** → Lưu UID thẻ vào danh sách thẻ lạ
3. **Thông báo trên web** → Alert màu vàng xuất hiện
4. **Admin xử lý**:
   - Thêm thẻ vào hệ thống nếu hợp lệ
   - Hoặc bỏ qua nếu là thẻ lạ

---

## 📊 Dữ Liệu Và Báo Cáo

### 📈 **Thống Kê Có Thể Xem**
- **Tổng số thẻ**: Số thẻ đã đăng ký trong hệ thống
- **Xe trong bãi**: Số xe hiện đang đỗ
- **Xe ngoài bãi**: Số xe không trong bãi
- **Tỷ lệ sử dụng**: % bãi xe đang được sử dụng
- **Hoạt động theo giờ**: Phân tích rush hour
- **Thời gian đỗ trung bình**: Xe đỗ bao lâu

### 💾 **Backup & Recovery**
- **Tự động backup**: Mỗi giờ hệ thống tự backup
- **Manual backup**: Admin có thể tạo backup bất cứ lúc nào
- **Restore**: Khôi phục dữ liệu từ backup khi cần
- **Export**: Xuất dữ liệu ra Excel/CSV

---

## 🔧 Bảo Trì Hệ Thống

### 🛠️ **Công Việc Thường Xuyên**
1. **Kiểm tra cảm biến**: ESP32 hoạt động đúng không
2. **Làm sạch dữ liệu**: Xóa log cũ, backup cũ
3. **Update thẻ**: Thêm thẻ mới cho xe mới
4. **Monitor**: Theo dõi error logs và performance

### ⚠️ **Xử Lý Sự Cố**
- **Mất kết nối ESP32**: Hệ thống chuyển sang manual mode
- **Thẻ bị lỗi**: Có thể thêm thẻ backup hoặc reset thẻ
- **Data corruption**: Khôi phục từ backup gần nhất
- **Server down**: Khởi động lại service hoặc restart máy

---

## 📱 Hướng Dẫn Truy Cập

### 🌐 **URL Truy Cập**
- **Local**: `http://localhost:5000`
- **Network**: `http://192.168.4.3:5000` (trong mạng WiFi UNO R4)
- **Mobile**: Responsive, có thể dùng trên điện thoại

### 🔑 **Phân Quyền**
- **User**: Xem thống kê, xem log
- **Admin**: Toàn quyền quản lý thẻ, backup, settings

### 📱 **Tính Năng Mobile**
- Responsive design cho mọi màn hình
- Touch-friendly interface
- Real-time notifications trên mobile
- Offline detection và auto-reconnect

---

## 🎯 Lợi Ích Của Hệ Thống

### ✨ **Cho Người Quản Lý**
- **Tự động hóa** 90% công việc quản lý bãi xe
- **Thống kê real-time** giúp ra quyết định nhanh
- **Audit trail** đầy đủ mọi hoạt động
- **Cảnh báo proactive** khi có vấn đề

### ✨ **Cho Người Dùng**
- **Nhanh chóng**: Không cần dừng xe lâu, chỉ quét thẻ
- **Tiện lợi**: Thẻ RFID nhỏ gọn, dễ mang theo
- **Minh bạch**: Có thể check thời gian đỗ xe
- **An toàn**: Chỉ thẻ đã đăng ký mới được vào

### ✨ **Cho Doanh Nghiệp**
- **Tiết kiệm nhân lực**: Giảm 80% nhân viên gác bãi
- **Tăng doanh thu**: Optimize việc sử dụng bãi xe
- **Dữ liệu phân tích**: Insight về pattern sử dụng
- **Scalable**: Dễ dàng mở rộng thêm vị trí

---

## 📞 Hỗ Trợ Kỹ Thuật

### 🆘 **Khi Gặp Vấn Đề**
1. **Check kết nối**: WiFi, Arduino, ESP32 có online không
2. **Xem error logs**: Trong tab Admin → System Logs
3. **Restart services**: Khởi động lại backend/frontend
4. **Restore backup**: Nếu dữ liệu bị lỗi
5. **Liên hệ support**: Nếu vẫn không giải quyết được

### 📋 **Thông Tin Cần Chuẩn Bị Khi Báo Lỗi**
- Thời gian xảy ra lỗi
- Thao tác đang thực hiện
- Error message (nếu có)
- Screenshot màn hình
- Log files từ system

---

*🎉 Chúc bạn sử dụng hiệu quả hệ thống BaiDoXe! 🚗*