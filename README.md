# 🅿️ Baidoxe - Parking Management System

Hệ thống quản lý bãi đỗ xe thông minh với backend API, giao diện web, và ứng dụng desktop.

## 📁 Cấu Trúc Dự Án

```
Baidoxe/
├── backend/          Flask API (Python)
├── frontend/         Web App (React)
├── desktop/          Desktop App (Electron)
├── hardware/         ESP32 & Arduino
└── scripts/          Tiện ích
```

## 🚀 Cài Đặt & Chạy

### Lần Đầu Tiên (Setup Một Lần)
```bash
SETUP.bat
```
Nó sẽ:
- Cài Python dependencies
- Cài Node.js dependencies
- Khởi tạo database SQLite
- Setup frontend & desktop

### Chạy Hệ Thống
```bash
START.bat
```
Nó sẽ:
- Khởi động Backend (Python) - localhost:5000
- Khởi động Frontend (React) - localhost:3000
- Tự động mở browser

## 📦 Thành Phần

| Phần | Công Nghệ | Cổng | Mô Tả |
|-----|-----------|------|-------|
| **Backend** | Flask + SQLAlchemy | 5000 | REST API |
| **Frontend** | React + TypeScript | 3000 | Web Dashboard |
| **Desktop** | Electron + React | N/A | App Desktop |
| **Database** | SQLite | N/A | parking_system.db |

### Backend Features
- ✅ Quản lý thẻ (thêm, xóa, danh sách)
- ✅ Theo dõi vị trí bãi
- ✅ Ghi log hoạt động
- ✅ Sao lưu & khôi phục dữ liệu

### Frontend Features
- ✅ Dashboard thống kê
- ✅ Quản lý thẻ
- ✅ Xem lịch sử quét
- ✅ Admin panel

### Desktop Features
- ✅ App native (Windows/Mac/Linux)
- ✅ Quản lý thẻ offline
- ✅ Xuất dữ liệu
- ✅ System tray

## 🔧 Công Nghệ

- **Backend:** Python 3.8+ / Flask / SQLAlchemy
- **Frontend:** React 18 / TypeScript
- **Desktop:** Electron 27 / Electron Builder
- **Hardware:** ESP32 / Arduino UNO R4 WiFi
- **Database:** SQLite3

## 📊 Tài Khoản Mặc Định

```
Username: admin
Password: admin123
```

## 📂 Các Folder Quan Trọng

| Folder | Mục Đích |
|--------|----------|
| `backend/data/` | Database & backup files |
| `backend/scripts/` | Khởi tạo & migrate data |
| `frontend/src/` | React source code |
| `desktop/src/` | Electron app source |
| `hardware/` | Firmware cho ESP32 & Arduino |

## 🛠️ Commands Hữu Ích

```bash
# Backend
cd backend
python run.py                    # Chạy API

# Frontend
cd frontend
npm run dev                      # Dev mode
npm run build                    # Build production

# Desktop
cd desktop
npm run dev                      # Dev mode
npm run build                    # Build installer
```

## 📝 Ghi Chú

- Dùng **SETUP.bat** để setup máy mới
- Dùng **START.bat** để chạy hệ thống
- Database tự động khởi tạo ở lần đầu
- Tất cả dữ liệu lưu ở `backend/data/parking_system.db`

## 📞 Liên Hệ

Baidoxe Development Team
