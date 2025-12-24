declare global {
  interface Window {
    electron: {
      // Backend management
      getBackendStatus: () => Promise<boolean>;
      shutdownBackend: () => Promise<boolean>;
      
      // Notifications
      showNotification: (options: {
        title: string;
        body: string;
        icon?: string;
      }) => Promise<'clicked' | 'closed'>;
      
      // File dialogs
      openFileDialog: (options?: {
        defaultPath?: string;
        filters?: Array<{ name: string; extensions: string[] }>;
        properties?: string[];
      }) => Promise<string | null>;
      
      saveFileDialog: (options?: {
        defaultPath?: string;
        filters?: Array<{ name: string; extensions: string[] }>;
      }) => Promise<string | null>;
      
      // Data export
      exportData: (data: any) => Promise<boolean>;
      
      // Updates
      checkUpdates: () => Promise<{ available: boolean; currentVersion: string }>;
      installUpdate: () => void;
      getAppVersion: () => Promise<{ version: string; name: string } | null>;
      
      // Update event listeners
      onUpdateAvailable: (callback: (data: any) => void) => void;
      onUpdateDownloaded: (callback: (data: any) => void) => void;
      onUpdateError: (callback: (data: any) => void) => void;
      onCheckingForUpdate: (callback: () => void) => void;
      
      // App info
      isElectron: boolean;
    };
  }
}

export {};
