# Native Features Guide

## Overview

Desktop app có access đến native Electron features thông qua `window.electron` object được expose qua preload script.

## Usage in React Components

### 1. Import Hook

```typescript
import useElectron from './useElectron';

function MyComponent() {
  const { showNotification, exportData, openFile, isElectron } = useElectron();
  
  // Use features
}
```

### 2. Available Methods

#### Show Notification
```typescript
await showNotification(title, body, icon?);

// Example
await showNotification('✅ Success', 'Operation completed successfully');
```

#### Open File Dialog
```typescript
const filePath = await openFile({
  defaultPath: '/path/to/default',
  filters: [
    { name: 'JSON Files', extensions: ['json'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});

// Returns: string (file path) or null if cancelled
```

#### Save File Dialog
```typescript
const filePath = await saveFile({
  defaultPath: '/path/to/default/file.json',
  filters: [{ name: 'JSON Files', extensions: ['json'] }]
});

// Returns: string (file path) or null if cancelled
```

#### Export Data
```typescript
const success = await exportData({
  cards: [...],
  logs: [...],
  timestamp: new Date().toISOString()
});

// Automatically opens save dialog and writes JSON file
// Returns: boolean (success/failure)
```

#### Get Backend Status
```typescript
const isRunning = await getBackendStatus();

// Returns: boolean
```

#### Check Updates
```typescript
const { available, currentVersion } = await checkUpdates();

// Returns: { available: boolean, currentVersion: string }
```

## Web vs Desktop

Native features automatically detect if running in Electron:

```typescript
if (useElectron().isElectron) {
  // Show native notification
} else {
  // Fallback: show in-app toast
}
```

## IPC Communication

All native features use IPC (Inter-Process Communication) which is secure and sandboxed.

### Main Process (`src/main.js`)
- Handles IPC requests
- Has access to native APIs
- Spawns Flask backend process

### Preload Script (`src/preload.js`)
- Exposes safe API to renderer process
- Acts as bridge
- Validates requests

### Renderer Process (React)
- Calls `window.electron.*` methods
- Gets responses via promises

## Adding New Native Features

1. **Add IPC handler in `src/main.js`:**
```javascript
ipcMain.handle('my-feature', async (event, params) => {
  // Do something native
  return result;
});
```

2. **Expose in `src/preload.js`:**
```javascript
contextBridge.exposeInMainWorld('electron', {
  myFeature: (params) => ipcRenderer.invoke('my-feature', params),
});
```

3. **Add TypeScript definition in `src/electron.d.ts`:**
```typescript
myFeature: (params: any) => Promise<any>;
```

4. **Add to `useElectron.ts` hook:**
```typescript
const myFeature = useCallback(async (params) => {
  if (!isElectron) return;
  return await window.electron?.myFeature(params);
}, [isElectron]);
```

## Security Notes

- Never expose sensitive operations without validation
- Always use contextIsolation = true in main.js
- Keep preload.js minimal and whitelist specific methods
- IPC handlers should validate all inputs
