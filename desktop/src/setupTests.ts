import '@testing-library/jest-dom';

// Mock window.electron for tests
Object.defineProperty(window, 'electron', {
  value: {
    isElectron: false,
    getBackendStatus: jest.fn(() => Promise.resolve(true)),
    shutdownBackend: jest.fn(() => Promise.resolve()),
    showNotification: jest.fn(() => Promise.resolve()),
    openFile: jest.fn(() => Promise.resolve(null)),
    saveFile: jest.fn(() => Promise.resolve('')),
    exportData: jest.fn(() => Promise.resolve('data.json')),
    checkUpdates: jest.fn(() => Promise.resolve(false)),
  },
  writable: true,
});

// Suppress console errors in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
        args[0].includes('Not implemented: HTMLFormElement.prototype.submit'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
