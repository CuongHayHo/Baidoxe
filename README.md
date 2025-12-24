# Baidoxe - IoT Parking Management System

Complete parking management system with backend API, web interface, and cross-platform desktop application.

## 📁 Project Structure

```
Baidoxe/
├── backend/              (Flask REST API)
├── frontend/             (React web app)
├── desktop/              (Electron desktop app)
├── hardware/             (ESP32 & Arduino sketches)
├── scripts/              (Utility scripts)
├── docs/                 (Documentation)
│   ├── TESTING_GUIDE.md  (Testing procedures)
│   ├── NATIVE_FEATURES.md (Electron native APIs)
│   ├── BUILD_GUIDE.md    (Build instructions)
│   └── ... (other docs)
├── MANUAL_TESTING_CHECKLIST.md
└── QA_GUIDELINES.md
```

## 🚀 Quick Start

### Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python run.py
# Backend runs on http://localhost:5000
```

### Frontend (React Web)

```bash
cd frontend
npm install
npm start
# Frontend runs on http://localhost:3000
```

### Desktop (Electron)

```bash
cd desktop
npm install
npm run dev
# Electron app launches with auto-started backend
```

## 📋 Components

### Backend
- Flask REST API server
- Card management (add, delete, list)
- Parking slot tracking
- Activity logging
- Backup & restore functionality
- Data import/export

### Frontend (Web)
- React dashboard
- Card management interface
- Parking slots visualization
- Activity logs viewer
- Admin panel

### Desktop (Electron)
- Electron app (Windows, macOS, Linux)
- React UI (reused from web version)
- Native OS notifications
- File dialogs
- Data export
- System tray integration
- Auto-start backend

### Hardware
- ESP32 RFID reader
- Arduino UNO R4 WiFi integration
- Real-time sensor data

## 🧪 Testing

### Run Tests

```bash
cd desktop

# Unit tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage

# E2E tests
npm run test:e2e

# Debug mode
npm run test:debug
```

### Test Documentation

- [TESTING_GUIDE.md](./desktop/TESTING_GUIDE.md) - Complete testing guide
- [MANUAL_TESTING_CHECKLIST.md](./MANUAL_TESTING_CHECKLIST.md) - Manual test checklist
- [QA_GUIDELINES.md](./QA_GUIDELINES.md) - QA process and standards

### Test Stack

- **Jest** - Unit testing framework
- **React Testing Library** - Component testing
- **Spectron** - Electron E2E testing
- **Playwright** - Alternative E2E testing

## 🏗️ Building

### Desktop Application

#### Windows
```bash
cd desktop
npm run build
# Creates: dist/Baidoxe-1.0.0.exe (NSIS installer)
#          dist/Baidoxe-1.0.0-x64-win.exe (Portable)
```

#### macOS
```bash
cd desktop
npm run build -- --mac
# Creates: dist/Baidoxe-1.0.0.dmg
#          dist/Baidoxe-1.0.0.zip
```

#### Linux
```bash
cd desktop
npm run build -- --linux
# Creates: dist/Baidoxe-1.0.0.AppImage
#          dist/baidoxe-1.0.0.deb
```

See [desktop/BUILD_GUIDE.md](./desktop/BUILD_GUIDE.md) for detailed build instructions.

## 📚 Documentation

### Setup & Development
- [Backend Setup](./backend/README.md) (if exists)
- [Frontend Setup](./frontend/README.md) (if exists)
- [Desktop Setup](./desktop/README.md)
- [Hardware Integration](./hardware/docs/hardware_solution.md)

### Building & Packaging
- [Build Guide](./desktop/BUILD_GUIDE.md)
- [Build Scripts](./scripts/) - Windows & Unix build helpers

### Features & Usage
- [Native Features Guide](./desktop/NATIVE_FEATURES.md)
- [API Documentation](./docs/)

### Testing & Quality
- [Testing Guide](./desktop/TESTING_GUIDE.md)
- [Manual Testing Checklist](./MANUAL_TESTING_CHECKLIST.md)
- [QA Guidelines](./QA_GUIDELINES.md)

## 🔧 Technology Stack

### Backend
- **Framework:** Flask (Python 3.8+)
- **Database:** JSON-based storage
- **APIs:** RESTful API with Flask-RESTX

### Frontend
- **Framework:** React 18.2.0
- **Language:** TypeScript
- **Styling:** CSS
- **HTTP Client:** Axios

### Desktop
- **Framework:** Electron 27.0.0
- **UI:** React (reused from web)
- **Build:** electron-builder
- **IPC:** Electron IPC with secure preload

### Hardware
- **Microcontrollers:** ESP32, Arduino UNO R4 WiFi
- **Sensors:** RFID readers
- **Protocol:** HTTP/WiFi

## 🔐 Security

- IPC communication secured with whitelist in preload.js
- CORS configuration in backend
- File dialog restrictions to prevent path traversal
- No credentials stored locally

## 📊 Testing & QA

### Automated Testing
- Unit tests with Jest
- Integration tests with React Testing Library
- E2E tests with Spectron
- Code coverage tracking

### Manual Testing
- Comprehensive test checklist
- Cross-platform testing (Windows, macOS, Linux)
- Performance benchmarking
- User acceptance testing

### QA Process
- Test case creation
- Bug tracking and reporting
- Performance metrics
- Regression testing
- Release sign-off

## 🌍 Cross-Platform Support

### Windows
- Windows 7 SP1+
- x64 and x86 architectures
- NSIS installer + Portable executable

### macOS
- macOS 10.12+
- Intel and Apple Silicon (native)
- DMG and ZIP distributions

### Linux
- Ubuntu, Fedora, Debian
- x64 and ARM64
- AppImage and DEB packages

## 📝 Development Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/feature-name
   # Make changes
   # Run tests: npm test
   # Commit changes
   git push origin feature/feature-name
   ```

2. **Testing**
   ```bash
   # Run full test suite
   npm test
   
   # Check coverage
   npm run test:coverage
   
   # Manual testing using checklist
   # See MANUAL_TESTING_CHECKLIST.md
   ```

3. **Building**
   ```bash
   cd desktop
   npm run build
   # Creates release artifacts
   ```

4. **Release**
   ```bash
   git tag v1.0.0
   git push origin --tags
   # Create release on GitHub
   # Upload build artifacts
   ```

## 🐛 Reporting Issues

Use GitHub Issues with:
- Clear title and description
- Reproduction steps
- Expected vs actual behavior
- Screenshots if applicable
- Build version and OS information

## 📄 License

MIT License

## 👥 Team

Baidoxe Development Team

## 📞 Support

For issues and questions:
1. Check documentation
2. Review test cases for examples
3. Check existing issues
4. Create new issue with detailed information

---

**Last Updated:** 2025-01-18  
**Current Version:** 1.0.0
