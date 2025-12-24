/**
 * Preload script
 * Cung cấp secure bridge giữa Electron main process và React renderer
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Backend management
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  shutdownBackend: () => ipcRenderer.invoke('shutdown-backend'),
  
  // Notifications
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  
  // File dialogs
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),
  
  // Data export/import
  exportData: (data) => ipcRenderer.invoke('export-data', data),
  
  // Updates
  checkUpdates: () => ipcRenderer.invoke('check-updates'),
  
  // App info
  isElectron: true,
});
