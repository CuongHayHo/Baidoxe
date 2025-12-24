/**
 * Electron Main Process
 * Quản lý window, menu, backend subprocess, auto-updater
 */

const { app, BrowserWindow, Menu, ipcMain, Tray, nativeTheme, dialog, Notification } = require('electron');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');
const isDev = require('electron-is-dev');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

let mainWindow;
let tray;
let backendProcess = null;

// URL backend
const BACKEND_URL = 'http://localhost:5000';
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Configure Auto-Updater
 */
if (!isDev) {
  // Configure logging
  autoUpdater.logger = log;
  autoUpdater.logger.transports.file.level = 'info';
  
  // Check for updates when app starts
  autoUpdater.checkForUpdatesAndNotify();
  
  // Check for updates every hour
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 60 * 60 * 1000);
  
  // Handle update events
  autoUpdater.on('update-available', (info) => {
    if (mainWindow) {
      mainWindow.webContents.send('update-available', {
        version: info.version,
        releaseDate: info.releaseDate
      });
      
      new Notification({
        title: 'Update Available',
        body: `Version ${info.version} is available. Downloading...`
      }).show();
    }
  });
  
  autoUpdater.on('update-downloaded', (info) => {
    if (mainWindow) {
      mainWindow.webContents.send('update-downloaded', {
        version: info.version
      });
    }
  });
  
  autoUpdater.on('error', (error) => {
    if (mainWindow) {
      mainWindow.webContents.send('update-error', {
        message: error.message
      });
    }
    log.error('Update error:', error);
  });
  
  autoUpdater.on('checking-for-update', () => {
    if (mainWindow) {
      mainWindow.webContents.send('checking-for-update');
    }
  });
}

/**
 * Tạo main window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
    icon: path.join(__dirname, '../public/favicon.ico'),
  });

  // Load app từ React dev server hoặc build folder
  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Hide khi close (tray mode)
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

/**
 * Tạo tray icon
 */
function createTray() {
  const icon = path.join(__dirname, '../public/favicon.ico');
  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  tray.setToolTip('Baidoxe - Parking Management');

  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });
}

/**
 * Tạo application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.isQuitting = true;
            app.quit();
          },
        },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Baidoxe',
              message: 'Baidoxe Parking Management System v1.0.0',
              detail: 'Desktop application for parking management',
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Start Flask backend
 */
async function startBackend() {
  try {
    // Kiểm tra xem backend có đang chạy không
    const axios = require('axios');
    const response = await axios.get(`${BACKEND_URL}/health`, { timeout: 2000 }).catch(() => null);
    
    if (response && response.status === 200) {
      console.log('✅ Backend already running');
      return true;
    }
  } catch (error) {
    console.log('Backend not running, starting...');
  }

  return new Promise((resolve) => {
    try {
      // Tìm đường dẫn Python
      const pythonPath = process.env.PYTHON_PATH || 'python';
      const backendDir = path.join(__dirname, '../../backend');

      // Start Flask server
      backendProcess = spawn(pythonPath, ['-m', 'backend.run'], {
        cwd: backendDir,
        stdio: 'inherit',
      });

      backendProcess.on('error', (error) => {
        console.error('Failed to start backend:', error);
        resolve(false);
      });

      // Chờ backend khởi động
      setTimeout(() => resolve(true), 3000);
    } catch (error) {
      console.error('Error starting backend:', error);
      resolve(false);
    }
  });
}

/**
 * App event handlers
 */
app.on('ready', async () => {
  // Start backend
  const backendReady = await startBackend();
  
  if (!backendReady) {
    console.warn('⚠️ Warning: Backend failed to start');
  }

  createWindow();
  createTray();
  createMenu();
});

app.on('window-all-closed', () => {
  // macOS behavior: keep app in dock
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
    mainWindow.focus();
  }
});

/**
 * IPC Handlers - Communication between Electron and React
 */

// Get backend status
ipcMain.handle('get-backend-status', async () => {
  try {
    const axios = require('axios');
    const response = await axios.get(`${BACKEND_URL}/health`, { timeout: 5000 });
    return response.status === 200;
  } catch {
    return false;
  }
});

// Shutdown backend gracefully
ipcMain.handle('shutdown-backend', () => {
  if (backendProcess) {
    backendProcess.kill();
    return true;
  }
  return false;
});

/**
 * Auto-Updater IPC Handlers
 */

// Check for updates
ipcMain.handle('check-updates', async () => {
  try {
    const result = await autoUpdater.checkForUpdates();
    return {
      updateAvailable: result?.updateInfo?.version !== app.getVersion(),
      currentVersion: app.getVersion(),
      newVersion: result?.updateInfo?.version,
      releaseDate: result?.updateInfo?.releaseDate
    };
  } catch (error) {
    log.error('Check updates error:', error);
    return { error: error.message };
  }
});

// Download and install update
ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});

// Get current version
ipcMain.handle('get-app-version', () => {
  return {
    version: app.getVersion(),
    name: 'Baidoxe'
  };
});

// Show notification
ipcMain.handle('show-notification', (event, options) => {
  return new Promise((resolve) => {
    const notification = new Notification(options);
    notification.show();
    
    notification.on('click', () => {
      resolve('clicked');
    });
    
    notification.on('close', () => {
      resolve('closed');
    });
  });
});

// Open file dialog
ipcMain.handle('open-file-dialog', async (event, options) => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      defaultPath: options?.defaultPath || app.getPath('documents'),
      filters: options?.filters || [{ name: 'All Files', extensions: ['*'] }],
      properties: ['openFile', ...(options?.properties || [])],
    });
    
    return result.canceled ? null : result.filePaths[0];
  } catch (error) {
    console.error('Error opening file dialog:', error);
    return null;
  }
});

// Save file dialog
ipcMain.handle('save-file-dialog', async (event, options) => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: options?.defaultPath || app.getPath('documents'),
      filters: options?.filters || [{ name: 'All Files', extensions: ['*'] }],
    });
    
    return result.canceled ? null : result.filePath;
  } catch (error) {
    console.error('Error saving file dialog:', error);
    return null;
  }
});

// Export data
ipcMain.handle('export-data', async (event, data) => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: path.join(app.getPath('documents'), `baidoxe_export_${new Date().toISOString().split('T')[0]}.json`),
      filters: [{ name: 'JSON Files', extensions: ['json'] }],
    });
    
    if (!result.canceled && result.filePath) {
      const fs = require('fs').promises;
      await fs.writeFile(result.filePath, JSON.stringify(data, null, 2));
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error exporting data:', error);
    return false;
  }
});

// Check update availability
ipcMain.handle('check-updates', async () => {
  // TODO: Implement auto-update logic
  return { available: false, currentVersion: app.getVersion() };
});

/**
 * Handle unhandled exceptions
 */
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});
