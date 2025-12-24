/**
 * useElectron Hook - Cho phép React components sử dụng Electron native features
 * Cung cấp wrapper functions để access native APIs một cách safe
 */

import { useCallback } from 'react';

export const useElectron = () => {
  const isElectron = typeof window !== 'undefined' && window.electron?.isElectron;

  const showNotification = useCallback(
    async (title: string, body: string, icon?: string) => {
      if (!isElectron) {
        console.log(`[Notification] ${title}: ${body}`);
        return;
      }

      try {
        await window.electron?.showNotification({
          title,
          body,
          icon,
        });
      } catch (error) {
        console.error('Failed to show notification:', error);
      }
    },
    [isElectron]
  );

  const openFile = useCallback(async (options?: any) => {
    if (!isElectron) {
      console.log('File dialog not available in web mode');
      return null;
    }

    try {
      return await window.electron?.openFileDialog(options);
    } catch (error) {
      console.error('Failed to open file dialog:', error);
      return null;
    }
  }, [isElectron]);

  const saveFile = useCallback(async (options?: any) => {
    if (!isElectron) {
      console.log('Save dialog not available in web mode');
      return null;
    }

    try {
      return await window.electron?.saveFileDialog(options);
    } catch (error) {
      console.error('Failed to open save dialog:', error);
      return null;
    }
  }, [isElectron]);

  const exportData = useCallback(async (data: any) => {
    if (!isElectron) {
      console.log('Export not available in web mode');
      return false;
    }

    try {
      return await window.electron?.exportData(data);
    } catch (error) {
      console.error('Failed to export data:', error);
      return false;
    }
  }, [isElectron]);

  const getBackendStatus = useCallback(async () => {
    if (!isElectron) {
      return false;
    }

    try {
      return await window.electron?.getBackendStatus();
    } catch (error) {
      console.error('Failed to get backend status:', error);
      return false;
    }
  }, [isElectron]);

  const checkUpdates = useCallback(async () => {
    if (!isElectron) {
      return { available: false, currentVersion: '0.0.0' };
    }

    try {
      return await window.electron?.checkUpdates();
    } catch (error) {
      console.error('Failed to check updates:', error);
      return { available: false, currentVersion: '0.0.0' };
    }
  }, [isElectron]);

  return {
    isElectron,
    showNotification,
    openFile,
    saveFile,
    exportData,
    getBackendStatus,
    checkUpdates,
  };
};

export default useElectron;
