# Build & Package Guide

## Overview

Desktop app sử dụng `electron-builder` để tạo installers cho các platform khác nhau.

## Prerequisites

- Node.js 16+
- Python 3.8+ (cho backend)
- npm hoặc yarn

### Platform-specific Requirements

**Windows:**
- Windows 7+
- No additional requirements

**macOS:**
- macOS 10.12+
- Xcode Command Line Tools (optional, cho signing)

**Linux:**
- Linux distribution với libappindicator hoặc libnotify
- For AppImage: glibc 2.14+

## Building

### 1. Setup

```bash
cd desktop
npm install
```

### 2. Development Build

Test app bằng Electron dev server:

```bash
npm run dev
```

This starts:
- React dev server (port 3000)
- Electron app
- Flask backend (auto-started)

### 3. Production Build

#### Build cho Windows

```bash
npm run build
```

Tạo ra:
- `dist/Baidoxe Setup 1.0.0.exe` - NSIS installer
- `dist/Baidoxe 1.0.0.exe` - Portable executable

#### Build cho macOS

```bash
npm run build -- --mac
```

Tạo ra:
- `dist/Baidoxe-1.0.0.dmg` - DMG installer
- `dist/Baidoxe-1.0.0.zip` - ZIP archive

#### Build cho Linux

```bash
npm run build -- --linux
```

Tạo ra:
- `dist/Baidoxe-1.0.0.AppImage` - AppImage executable
- `dist/baidoxe_1.0.0_amd64.deb` - DEB package

#### Build cho All Platforms

```bash
npm run build -- -mwl
```

## Distribution Configuration

### Build Output Structure

```
desktop/
├── build/              (React production build)
├── dist/               (Final distributables)
│   ├── Baidoxe Setup 1.0.0.exe      (Windows NSIS)
│   ├── Baidoxe 1.0.0.exe            (Windows portable)
│   ├── Baidoxe-1.0.0.dmg            (macOS)
│   ├── Baidoxe-1.0.0.AppImage       (Linux)
│   └── baidoxe_1.0.0_amd64.deb      (Linux DEB)
```

### Configuration Files

**package.json** - Main configuration:
```json
{
  "build": {
    "appId": "com.baidoxe.app",
    "productName": "Baidoxe",
    "files": ["build/**/*", "src/main.js", ...],
    "win": { /* Windows config */ },
    "mac": { /* macOS config */ },
    "linux": { /* Linux config */ },
    "nsis": { /* Windows installer */ },
    "deb": { /* Linux package */ }
  }
}
```

## Advanced Build Options

### Code Signing (Optional)

#### Windows Code Signing

```bash
npm run build -- --win --sign=path/to/certificate.pfx
```

#### macOS Code Signing

Set environment variables:
```bash
export CSC_LINK=path/to/certificate.p12
export CSC_KEY_PASSWORD=password
npm run build -- --mac
```

### Custom Output Directory

```bash
npm run build -- --publish=never --output=./release
```

### Debug Build

```bash
DEBUG=electron-builder npm run build
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - run: cd desktop && npm install
      - run: cd desktop && npm run build
      
      - uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: desktop/dist/
```

## Troubleshooting

### Build fails with "Cannot find module"

```bash
# Clean and rebuild
rm -rf node_modules build dist
npm install
npm run build
```

### Windows NSIS installer issues

- Ensure all files are properly built in `build/` folder
- Check that `src/main.js` and `src/preload.js` exist
- Verify icon files exist in `public/`

### macOS notarization issues

Apple requires code signing for macOS apps. For distribution:

```bash
export APPLE_ID=your-email@example.com
export APPLE_PASSWORD=your-app-specific-password
export TEAM_ID=your-team-id
npm run build -- --mac --publish=always
```

### Linux AppImage permissions

```bash
chmod +x dist/Baidoxe-*.AppImage
./dist/Baidoxe-*.AppImage
```

## Release Workflow

1. Update version in `package.json`
2. Build for all platforms:
   ```bash
   npm run build -- -mwl
   ```
3. Test installers on each platform
4. Create GitHub release with built files
5. Publish to download server or app store

## File Size Optimization

Default build size: ~200-300 MB (includes Chromium + Python backend)

To reduce:
- Remove unused dependencies
- Enable asar archiving (automatic)
- Use uglify/minify (automatic)

## Update Strategy

See [NATIVE_FEATURES.md](./NATIVE_FEATURES.md) for auto-update implementation.
