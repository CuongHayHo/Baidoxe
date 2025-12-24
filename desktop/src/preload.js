/**
 * Preload script
 * Cung cấp secure bridge giữa Electron main process và React renderer
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Backend management
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  shutdownBackend: () => ipcRenderer.invoke('shutdown-backend'),
  
  // App info
  isElectron: true,
});
