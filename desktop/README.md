# Baidoxe Desktop App

Electron-based desktop application for Baidoxe parking management system.

## Features

- 🖥️ Native desktop application using Electron
- ⚛️ React UI reused from web version
- 🔌 Auto-start Flask backend
- 🎯 System tray integration
- � Native notifications
- 📂 File dialogs
- 💾 Data export
- 💻 Windows, macOS, Linux support

## Quick Start

### Prerequisites

- Node.js 16+
- Python 3.8+

### Installation

```bash
cd desktop
npm install
```

### Development

```bash
npm run dev
```

Starts:
- React dev server (port 3000)
- Electron app
- Flask backend (auto-started)

### Build

```bash
# Windows
npm run build

# macOS
npm run build -- --mac

# Linux
npm run build -- --linux

# All platforms
npm run build -- -mwl
```

Or use build scripts:

```bash
# Windows
./build.bat windows

# Unix/Linux/macOS
./build.sh windows
```

## Project Structure

```
desktop/
├── src/
│   ├── main.js          (Electron main process)
│   ├── preload.js       (IPC bridge)
│   ├── App.tsx          (Main UI)
│   ├── api.ts           (API client)
│   ├── useElectron.ts   (Native features hook)
│   └── types.ts
├── public/
│   └── index.html
├── build/               (React build output)
├── dist/                (Final executables)
├── package.json
├── tsconfig.json
├── BUILD_GUIDE.md       (Detailed build documentation)
├── NATIVE_FEATURES.md   (Native API documentation)
└── README.md
```

## Documentation

- [BUILD_GUIDE.md](./BUILD_GUIDE.md) - Complete build & packaging guide
- [NATIVE_FEATURES.md](./NATIVE_FEATURES.md) - Native Electron features guide

## Architecture

### Main Process (Node.js)
- Manages windows, menus, tray
- Spawns Flask backend
- Handles IPC requests
- Access to native APIs

### Preload Script (Sandbox)
- Secure bridge between main and renderer
- Exposes safe API methods
- IPC communication

### Renderer Process (React)
- UI components
- Uses `window.electron` for native features
- Communicates via IPC

### Backend (Python)
- Flask server (port 5000)
- Auto-started by Electron
- Same backend as web version

## Development Tips

### Using Native Features

```typescript
import useElectron from './useElectron';

function MyComponent() {
  const { showNotification, openFile, exportData } = useElectron();
  
  const handleExport = async () => {
    const success = await exportData(data);
  };
}
```

### Add New Native Feature

1. Add IPC handler in `src/main.js`
2. Expose in `src/preload.js`
3. Add type in `src/electron.d.ts`
4. Add helper in `src/useElectron.ts`

See [NATIVE_FEATURES.md](./NATIVE_FEATURES.md) for details.

## Troubleshooting

### Backend fails to start

- Ensure Python 3.8+ is installed
- Check Flask installation: `python -m pip install flask`
- Verify backend path is correct in `src/main.js`

### Build fails

```bash
# Clean and rebuild
rm -rf node_modules build dist
npm install
npm run build
```

### Development server issues

- Kill any existing node processes
- Clear React cache: `rm -rf build`
- Reinstall: `npm install`

## Performance

- App size: ~200-300 MB (includes Chromium + backend)
- Startup time: ~3-5 seconds
- Memory usage: ~150-200 MB baseline

## License

MIT

## Support

For issues and feature requests, create an issue in the main repository.
