declare global {
  interface Window {
    electron: {
      getBackendStatus: () => Promise<boolean>;
      shutdownBackend: () => Promise<boolean>;
      isElectron: boolean;
    };
  }
}

export {};
