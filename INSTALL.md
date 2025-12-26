# 📦 Hướng Dẫn Cài Đặt Baidoxe Parking Management System

## 📋 Yêu Cầu Hệ Thống

### Bắt Buộc
- **Node.js**: v16.x hoặc cao hơn
- **Python**: v3.8 hoặc cao hơn
- **Git**: Phiên bản mới nhất

### Tùy Chọn
- **Windows**: Để build desktop app
- **Visual C++ Build Tools**: Cho Windows (cần cho một số native modules)

---

## 🚀 Cài Đặt Nhanh

### 1. Clone Repository
```bash
git clone <repository-url>
cd Baidoxe
```

### 2. Cài Đặt Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python run.py
```

Backend sẽ chạy trên `http://localhost:5000`

### 3. Cài Đặt Frontend Web
```bash
cd frontend
npm install
npm start
```

Frontend sẽ mở trên `http://localhost:3000`

### 4. Cài Đặt Desktop App (Tùy Chọn)
```bash
cd desktop
npm install
npm run dev
```

---

## 📝 Cài Đặt Chi Tiết

### Backend Setup

#### Windows
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### macOS/Linux
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Chạy Backend
```bash
# Development
python run.py

# Production (với gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**API Documentation**: `http://localhost:5000/api/docs`

---

### Frontend Web Setup

```bash
cd frontend

# Cài đặt dependencies
npm install

# Phát triển (development)
npm start

# Build production
npm run build

# Test
npm test
```

**Lưu ý**: `.npmrc` file có sẵn để tự động dùng `legacy-peer-deps`

---

### Desktop App Setup

```bash
cd desktop

# Cài đặt dependencies
npm install

# Phát triển (Electron + React)
npm run dev

# Build production
npm run build

# Build installer (Windows/macOS)
npm run dist
```

**Lưu ý**: Cần Electron builder để build desktop app

---

## ⚙️ Cấu Hình

### Environment Variables

#### Backend (`.env` hoặc `config/config.py`)
```python
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///data/parking_system.db
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

#### Frontend (`.env`)
```
REACT_APP_API_URL=http://localhost:5000
```

#### Desktop (`.env`)
```
REACT_APP_API_URL=http://localhost:5000
```

---

## 🗄️ Database

### Khởi Tạo Database
```bash
cd backend
python scripts/init_db.py
```

### Migrate Dữ Liệu từ JSON
```bash
python scripts/migrate_json_to_db.py
```

### Reset Database
```bash
# Xóa file database
rm data/parking_system.db

# Tạo lại
python scripts/init_db.py
```

---

## 🧪 Kiểm Tra Cài Đặt

### Backend
```bash
# Kiểm tra API
curl http://localhost:5000/api/system/health
```

### Frontend
```bash
# Kiểm tra build
npm run build
```

### Desktop
```bash
# Kiểm tra build
npm run react-build
```

---

## 🐛 Troubleshooting

### Backend

**Lỗi: `ModuleNotFoundError`**
```bash
# Đảm bảo virtual environment được activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Cài lại dependencies
pip install -r requirements.txt
```

**Lỗi: Port 5000 đang dùng**
```bash
# Thay đổi port trong config hoặc
python run.py --port 8000
```

### Frontend

**Lỗi: `npm install` fails**
```bash
# Xóa node_modules và package-lock.json
rm -rf node_modules package-lock.json

# Cài lại
npm install
```

**Lỗi: `legacy-peer-deps`**
```bash
# .npmrc file đã có sẵn, nếu cần cài lại:
npm install --legacy-peer-deps
```

### Desktop

**Lỗi: Electron không khởi động**
```bash
# Kiểm tra Node version
node --version  # Cần v16+

# Xóa cache
rm -rf node_modules package-lock.json

# Cài lại
npm install
npm run dev
```

**Lỗi: Build fails**
```bash
# Đảm bảo dependencies đúng
npm install --legacy-peer-deps

# Clean build
npm run react-build
npm run build
```

### CORS Issues

Nếu gặp CORS errors, kiểm tra `backend/config/cors.py`:
```python
CORS_ORIGINS = [
    "http://localhost:3000",      # Frontend
    "http://localhost:8080",      # Desktop dev
    "file://",                     # Desktop production
]
```

---

## 📊 Kiến Trúc Hệ Thống

```
Baidoxe/
├── backend/                 # Python Flask API
│   ├── api/                # API endpoints
│   ├── models/             # SQLAlchemy models
│   ├── services/           # Business logic
│   ├── config/             # Configuration
│   └── data/               # SQLite database & JSON files
│
├── frontend/               # React web app
│   ├── src/
│   ├── public/
│   └── build/              # Production build
│
├── desktop/                # Electron desktop app
│   ├── src/
│   ├── build/              # Desktop build
│   └── dist/               # Installer
│
└── docs/                   # Documentation
```

---

## 🔄 Quy Trình Khởi Động

### Development (3 Terminal)

**Terminal 1 - Backend**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm start
```

**Terminal 3 - Desktop (tùy chọn)**
```bash
cd desktop
npm run dev
```

### Production

```bash
# Build frontend
cd frontend && npm run build

# Build desktop
cd desktop && npm run build

# Chạy backend (production mode)
cd backend && gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📚 Tài Liệu Thêm

- [README.md](./README.md) - Tổng quan dự án
- [docs/HUONG_DAN_SU_DUNG_WEBSITE.md](./docs/HUONG_DAN_SU_DUNG_WEBSITE.md) - Hướng dẫn sử dụng
- [docs/GIAI_THICH_CODE_VA_KIEN_TRUC.md](./docs/GIAI_THICH_CODE_VA_KIEN_TRUC.md) - Giải thích kiến trúc
- [desktop/BUILD_GUIDE.md](./desktop/BUILD_GUIDE.md) - Build guide cho desktop
- [desktop/TESTING_GUIDE.md](./desktop/TESTING_GUIDE.md) - Testing guide

---

## ✅ Checklist Cài Đặt

- [ ] Clone repository
- [ ] Cài Python 3.8+
- [ ] Cài Node.js 16+
- [ ] Cài backend dependencies (`pip install -r requirements.txt`)
- [ ] Khởi tạo database (`python scripts/init_db.py`)
- [ ] Cài frontend dependencies (`npm install`)
- [ ] Chạy backend (`python run.py`)
- [ ] Chạy frontend (`npm start`)
- [ ] Kiểm tra API (`http://localhost:5000/api/system/health`)
- [ ] Kiểm tra Web UI (`http://localhost:3000`)
- [ ] Cài desktop app (tùy chọn)

---

## 🤝 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra các yêu cầu hệ thống
2. Xem phần Troubleshooting
3. Kiểm tra logs trong `backend/logs/` hoặc console
4. Liên hệ đội phát triển

---

**Last Updated**: December 26, 2025
