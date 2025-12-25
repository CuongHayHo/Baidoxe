/**
 * Preload script
 * Cung cấp secure bridge giữa Electron main process và React renderer
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Backend management
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  shutdownBackend: () => ipcRenderer.invoke('shutdown-backend'),
  
  // External links
  openExternalLink: (url) => ipcRenderer.send('open-external-link', url),
  
  // Notifications
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  
  // File dialogs
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),
  
  // Data export/import
  exportData: (data) => ipcRenderer.invoke('export-data', data),
  
  // Auto-Updater
  checkUpdates: () => ipcRenderer.invoke('check-updates'),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  onUpdateAvailable: (callback) => 
    ipcRenderer.on('update-available', (_, data) => callback(data)),
  onUpdateDownloaded: (callback) => 
    ipcRenderer.on('update-downloaded', (_, data) => callback(data)),
  onUpdateError: (callback) => 
    ipcRenderer.on('update-error', (_, data) => callback(data)),
  onCheckingForUpdate: (callback) => 
    ipcRenderer.on('checking-for-update', () => callback()),
  
  // App info
  isElectron: true,
});
