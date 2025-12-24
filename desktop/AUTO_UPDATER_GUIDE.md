# Auto-Updater & Installer Setup

## Overview

Complete auto-update system for Baidoxe desktop app using electron-updater with staged rollouts, version checking, and update notifications.

## Architecture

### Update Flow

```
┌─────────────────────────────────────────────┐
│         App Starts                          │
│  (electron-updater checks for updates)      │
└────────────┬────────────────────────────────┘
             │
             ├─ No Update: Run normally
             │
             └─ Update Available:
                ├─ Show notification
                ├─ Download update
                ├─ Verify signature
                ├─ Show "Restart to Update" dialog
                └─ Install on restart
```

### Update Server

Uses GitHub releases as free update server:
- Upload new version to GitHub Releases
- electron-updater automatically finds it
- Supports staged rollouts (% of users)
- Tracks analytics (optional)

## Installation

```bash
npm install electron-updater
```

## Configuration

### package.json Build Config

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-username",
      "repo": "baidoxe"
    }
  }
}
```

## Implementation

### Main Process (src/main.js)

```javascript
import { app, BrowserWindow, ipcMain } from 'electron';
import { autoUpdater } from 'electron-updater';
import log from 'electron-log';

// Configure logging
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';

function setupUpdater() {
  autoUpdater.checkForUpdatesAndNotify();
  
  // Check for updates every hour
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 60 * 60 * 1000);
}

// IPC: Check for updates manually
ipcMain.handle('check-updates', async () => {
  try {
    const result = await autoUpdater.checkForUpdates();
    return {
      updateAvailable: result?.updateInfo?.version !== app.getVersion(),
      currentVersion: app.getVersion(),
      newVersion: result?.updateInfo?.version
    };
  } catch (error) {
    return { error: error.message };
  }
});

// IPC: Download and install update
ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});

// Update events
autoUpdater.on('update-available', (info) => {
  mainWindow.webContents.send('update-available', {
    version: info.version,
    releaseDate: info.releaseDate
  });
});

autoUpdater.on('update-downloaded', (info) => {
  mainWindow.webContents.send('update-downloaded', {
    version: info.version
  });
});

autoUpdater.on('error', (error) => {
  mainWindow.webContents.send('update-error', {
    message: error.message
  });
});

autoUpdater.on('checking-for-update', () => {
  mainWindow.webContents.send('checking-for-update');
});

// Call on app ready
app.on('ready', () => {
  setupUpdater();
});
```

### Preload (src/preload.js)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // ... existing code ...
  
  // Update APIs
  checkUpdates: () => ipcRenderer.invoke('check-updates'),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  onUpdateAvailable: (callback) => 
    ipcRenderer.on('update-available', (_, data) => callback(data)),
  onUpdateDownloaded: (callback) => 
    ipcRenderer.on('update-downloaded', (_, data) => callback(data)),
  onUpdateError: (callback) => 
    ipcRenderer.on('update-error', (_, data) => callback(data)),
  onCheckingForUpdate: (callback) => 
    ipcRenderer.on('checking-for-update', () => callback()),
});
```

### React Component (src/components/UpdateNotification.tsx)

```typescript
import React, { useEffect, useState } from 'react';
import useElectron from '../useElectron';

interface UpdateStatus {
  available: boolean;
  downloaded: boolean;
  version?: string;
  error?: string;
}

export default function UpdateNotification() {
  const { isElectron } = useElectron();
  const [updateStatus, setUpdateStatus] = useState<UpdateStatus>({
    available: false,
    downloaded: false,
  });

  useEffect(() => {
    if (!isElectron) return;

    const electron = (window as any).electron;

    // Listen for update events
    electron.onCheckingForUpdate?.(() => {
      setUpdateStatus((prev) => ({ ...prev }));
    });

    electron.onUpdateAvailable?.((data: any) => {
      setUpdateStatus({
        available: true,
        downloaded: false,
        version: data.version,
      });
      
      // Show notification
      electron.showNotification?.(
        'Update Available',
        `Version ${data.version} is available. Downloading...`
      );
    });

    electron.onUpdateDownloaded?.((data: any) => {
      setUpdateStatus({
        available: true,
        downloaded: true,
        version: data.version,
      });
    });

    electron.onUpdateError?.((data: any) => {
      setUpdateStatus((prev) => ({
        ...prev,
        error: data.message,
      }));
    });

    // Check for updates on mount
    electron.checkUpdates?.();
  }, [isElectron]);

  if (!updateStatus.downloaded) return null;

  return (
    <div className="update-notification">
      <div className="update-banner">
        <div className="update-content">
          <h3>Update Available</h3>
          <p>Version {updateStatus.version} is ready to install.</p>
        </div>
        <div className="update-actions">
          <button
            onClick={() => {
              const electron = (window as any).electron;
              electron.installUpdate?.();
            }}
            className="btn-primary"
          >
            Restart & Update
          </button>
          <button onClick={() => setUpdateStatus((prev) => ({ ...prev, downloaded: false }))} className="btn-secondary">
            Later
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Add to App.tsx

```typescript
import UpdateNotification from './components/UpdateNotification';

export default function App() {
  return (
    <>
      <UpdateNotification />
      {/* ... rest of app ... */}
    </>
  );
}
```

### CSS (src/UpdateNotification.css)

```css
.update-notification {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  z-index: 1000;
}

.update-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.update-content {
  flex: 1;
}

.update-content h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.update-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.update-actions {
  display: flex;
  gap: 12px;
  margin-left: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: white;
  color: #667eea;
  font-weight: 600;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}
```

## Release Management

### Creating a Release

```bash
# 1. Bump version in package.json
npm version patch  # or minor, major

# 2. Build for all platforms
npm run build

# 3. Create GitHub release
git tag v1.0.1
git push origin --tags

# 4. Upload release artifacts
# Go to GitHub Releases page
# Create new release for v1.0.1
# Upload .exe, .dmg, .AppImage files
# Publish release

# electron-updater will automatically find it
```

### GitHub Release Best Practices

**Title:** `Version 1.0.1`

**Body:**
```markdown
## Features
- Feature 1
- Feature 2

## Bug Fixes
- Bug fix 1
- Bug fix 2

## Installation
Windows: Download `Baidoxe-1.0.1.exe`
macOS: Download `Baidoxe-1.0.1.dmg`
Linux: Download `Baidoxe-1.0.1.AppImage`

## Changes
- Change 1
- Change 2
```

**Assets to Upload:**
- `Baidoxe-1.0.1.exe` (Windows NSIS installer)
- `Baidoxe-1.0.1-x64-win.exe` (Windows portable)
- `Baidoxe-1.0.1.dmg` (macOS)
- `Baidoxe-1.0.1.AppImage` (Linux)
- `latest.yml` (auto-updater metadata)

## Advanced Configuration

### Staged Rollout

```javascript
const updateInfo = await autoUpdater.checkForUpdates();

// Only update 10% of users
if (Math.random() < 0.1) {
  autoUpdater.downloadUpdate();
}
```

### Custom Update Server

Instead of GitHub, use your own server:

```json
{
  "build": {
    "publish": {
      "provider": "generic",
      "url": "https://updates.example.com/releases/"
    }
  }
}
```

Server structure:
```
https://updates.example.com/releases/
├── latest.yml
├── Baidoxe-1.0.1.exe
├── Baidoxe-1.0.1.dmg
└── Baidoxe-1.0.1.AppImage
```

### Differential Updates

Only download changed files:

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "releaseType": "release"
    },
    "files": [
      "build/**/*",
      "node_modules/**/*",
      "src/main.js",
      "package.json"
    ]
  }
}
```

## Troubleshooting

### Update Not Found

1. Verify GitHub release exists
2. Check version in package.json is newer
3. Ensure assets uploaded correctly
4. Check network connectivity
5. Review logs in `%APPDATA%/Baidoxe/logs/`

### Update Signature Invalid

1. Sign releases with certificate
2. Upload signature files to release
3. Configure signing in package.json

### Rollback

If update causes issues:

```javascript
// In main.js
const previousVersion = '1.0.0';
if (app.getVersion() === '1.0.1') {
  // Known issues, prevent auto-update
  autoUpdater.isUpdaterActive = false;
}
```

## Testing Updates

### Test Locally

```javascript
// In main.js for development
if (isDev) {
  autoUpdater.updateConfigPath = path.join(
    __dirname,
    'dev-app-update.yml'
  );
}
```

### Create Test Release

1. Create beta version (e.g., 1.0.1-beta.1)
2. Upload to GitHub Releases as pre-release
3. Test with limited users
4. Fix issues
5. Release final version

### Manual Update Testing

```javascript
ipcMain.handle('test-update', async () => {
  const result = await autoUpdater.checkForUpdates();
  return {
    found: !!result?.updateInfo,
    info: result?.updateInfo
  };
});
```

## Analytics

### Track Update Adoption

```javascript
autoUpdater.on('update-downloaded', () => {
  // Send analytics
  fetch('https://analytics.example.com/update', {
    method: 'POST',
    body: JSON.stringify({
      app: 'baidoxe',
      version: app.getVersion(),
      newVersion: updateInfo?.version,
      platform: process.platform,
      timestamp: new Date()
    })
  });
});
```

## Security

### Code Signing

**macOS:**
```json
{
  "build": {
    "mac": {
      "identity": "Developer ID Application",
      "certificateFile": "certificate.p12",
      "certificatePassword": "${CSC_KEY_PASSWORD}"
    }
  }
}
```

**Windows:**
```json
{
  "build": {
    "win": {
      "certificateFile": "certificate.pfx",
      "certificatePassword": "${CSC_KEY_PASSWORD}",
      "signingHashAlgorithms": ["sha256"],
      "sign": "./customSign.js"
    }
  }
}
```

### Signature Verification

electron-updater automatically verifies signatures using:
- ASAR integrity checking
- Signature verification for macOS/Windows
- Hash verification for all platforms

## Release Checklist

- [ ] Update version in package.json
- [ ] Update CHANGELOG.md with new features/fixes
- [ ] Run full test suite
- [ ] Build for all platforms
- [ ] Test each build locally
- [ ] Create GitHub release
- [ ] Upload all artifacts
- [ ] Test auto-update on each platform
- [ ] Monitor for user reports
- [ ] Document any issues

## Maintenance

### Clean Up Old Releases

```bash
# Keep only last 5 releases
git tag -l | sort -V | head -n -5 | xargs git tag -d
```

### Version Bumping

```bash
# Patch (1.0.0 → 1.0.1)
npm version patch

# Minor (1.0.0 → 1.1.0)
npm version minor

# Major (1.0.0 → 2.0.0)
npm version major
```

## Resources

- [electron-updater docs](https://www.electron.build/auto-update)
- [Electron security](https://www.electronjs.org/docs/tutorial/security)
- [GitHub releases API](https://docs.github.com/en/repositories/releasing-projects-on-github)
