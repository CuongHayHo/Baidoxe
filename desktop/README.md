# Baidoxe Desktop App

Electron-based desktop application for Baidoxe parking management system.

## Features

- 🖥️ Native desktop application using Electron
- ⚛️ React UI reused from web version
- 🔌 Auto-start Flask backend
- 🎯 System tray integration
- 💻 Windows, macOS, Linux support

## Setup

### Prerequisites

- Node.js 16+
- Python 3.8+
- Windows 10+ / macOS / Linux

### Installation

1. Navigate to desktop folder:
```bash
cd desktop
npm install
```

2. Copy React components to desktop/src/components:
```bash
cp -r ../frontend/src/components ./src/
cp ../frontend/src/api.ts ./src/
cp ../frontend/src/types.ts ./src/
```

### Development

```bash
npm run dev
```

This will start:
- React dev server on port 3000
- Electron app
- Flask backend (auto-started)

### Building

```bash
npm run build
```

This creates:
- Windows installer (NSIS)
- Portable executable

### Notes

- Backend is auto-started when app opens
- If backend fails to start, app will warn but continue
- Backend runs on port 5000
- Desktop app reuses all frontend React components
