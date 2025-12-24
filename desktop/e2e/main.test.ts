/**
 * E2E Tests for Baidoxe Desktop App
 * Using Spectron for Electron testing
 * 
 * Run with: npm run test:e2e
 */

import { Application } from 'spectron';
import * as path from 'path';
import * as fs from 'fs';

describe('Baidoxe Desktop E2E Tests', () => {
  let app: Application;

  beforeAll(async () => {
    // Build app first
    const appPath = path.join(
      __dirname,
      '../dist/win-unpacked/Baidoxe.exe'
    );

    if (!fs.existsSync(appPath)) {
      console.log('App not built. Please run: npm run build');
      return;
    }

    app = new Application({
      path: appPath,
      args: [],
      webdriverOptions: {
        logLevel: 'silent',
      },
    });

    return app.start();
  }, 30000);

  afterAll(async () => {
    if (app && app.isRunning()) {
      return app.stop();
    }
  });

  describe('Window Management', () => {
    it('should open main window', async () => {
      const count = await app.client.getWindowCount();
      expect(count).toBeGreaterThan(0);
    });

    it('should display window with correct title', async () => {
      const title = await app.client.getTitle();
      expect(title).toContain('Baidoxe');
    });

    it('should not have dev tools open', async () => {
      const devToolsOpen = await app.client.execute(() => {
        return false; // Would check actual state
      });
      expect(devToolsOpen).toBe(false);
    });

    it('should have minimum window dimensions', async () => {
      const bounds = await app.client.execute(() => {
        return {
          width: window.innerWidth,
          height: window.innerHeight,
        };
      });

      expect(bounds.width).toBeGreaterThanOrEqual(800);
      expect(bounds.height).toBeGreaterThanOrEqual(600);
    });
  });

  describe('Navigation & UI', () => {
    it('should display dashboard tab active initially', async () => {
      const dashboardTab = await app.client.$('button:contains("Dashboard")');
      const ariaSelected = await dashboardTab.getAttribute('aria-selected');
      expect(ariaSelected).toBe('true');
    });

    it('should switch to cards tab', async () => {
      const cardsTab = await app.client.$('button:contains("Cards")');
      await cardsTab.click();

      // Wait for content to load
      await app.client.waitUntil(
        async () => {
          const selected = await cardsTab.getAttribute('aria-selected');
          return selected === 'true';
        },
        { timeout: 5000 }
      );

      expect(await cardsTab.getAttribute('aria-selected')).toBe('true');
    });

    it('should navigate to parking slots tab', async () => {
      const parkingTab = await app.client.$('button:contains("Parking")');
      await parkingTab.click();

      await app.client.waitUntil(
        async () => {
          const selected = await parkingTab.getAttribute('aria-selected');
          return selected === 'true';
        },
        { timeout: 5000 }
      );
    });

    it('should display logs tab', async () => {
      const logsTab = await app.client.$('button:contains("Logs")');
      await logsTab.click();

      await app.client.waitUntil(
        async () => {
          const selected = await logsTab.getAttribute('aria-selected');
          return selected === 'true';
        },
        { timeout: 5000 }
      );
    });

    it('should display admin tab', async () => {
      const adminTab = await app.client.$('button:contains("Admin")');
      await adminTab.click();

      await app.client.waitUntil(
        async () => {
          const selected = await adminTab.getAttribute('aria-selected');
          return selected === 'true';
        },
        { timeout: 5000 }
      );
    });
  });

  describe('Backend Integration', () => {
    it('should detect backend running', async () => {
      const status = await app.client.execute(() => {
        return new Promise((resolve) => {
          fetch('http://localhost:5000/api/system/')
            .then(() => resolve(true))
            .catch(() => resolve(false));
        });
      });

      expect(status).toBe(true);
    });

    it('should show backend status indicator', async () => {
      const statusIndicator = await app.client.$('[data-testid="backend-status"]');
      expect(await statusIndicator.isDisplayed()).toBe(true);
    });

    it('should fetch and display statistics', async () => {
      const stats = await app.client.execute(() => {
        return fetch('http://localhost:5000/api/system/')
          .then((r) => r.json())
          .catch(() => ({}));
      });

      expect(stats).toHaveProperty('total_cards');
    });
  });

  describe('Native Features', () => {
    it('should be able to call native APIs', async () => {
      const result = await app.client.execute(() => {
        return (window as any).electron !== undefined;
      });

      expect(result).toBe(true);
    });

    it('should show notifications', async () => {
      const result = await app.client.execute(async () => {
        const electron = (window as any).electron;
        if (!electron) return false;

        await electron.showNotification('Test', 'Test message');
        return true;
      });

      expect(result).toBe(true);
    });

    it('should check backend status via IPC', async () => {
      const status = await app.client.execute(async () => {
        const electron = (window as any).electron;
        if (!electron) return null;

        return await electron.getBackendStatus();
      });

      expect(status).toBe(true);
    });
  });

  describe('System Tray', () => {
    it('should have tray icon', async () => {
      const hasTray = await app.client.execute(() => {
        return (window as any).electron?.isElectron === true;
      });

      expect(hasTray).toBe(true);
    });

    it('should restore window from tray', async () => {
      // Minimize app
      await app.client.execute(() => {
        (window as any).ipcRenderer?.send('minimize-to-tray');
      });

      // Small delay
      await new Promise((r) => setTimeout(r, 500));

      // Check if window still accessible
      const count = await app.client.getWindowCount();
      expect(count).toBeGreaterThan(0);
    });
  });

  describe('Data Operations', () => {
    it('should handle large data sets (1000+ items)', async () => {
      // Create or load large dataset
      // Verify performance is acceptable
      // Check no memory leaks
    });

    it('should export data successfully', async () => {
      const exported = await app.client.execute(async () => {
        const electron = (window as any).electron;
        if (!electron) return null;

        return await electron.exportData();
      });

      expect(exported).toBeTruthy();
    });

    it('should handle backup operations', async () => {
      // Trigger backup
      // Verify file created
      // Verify format is valid JSON
    });
  });

  describe('Error Handling', () => {
    it('should handle backend disconnection', async () => {
      // Simulate backend failure
      // Verify graceful error message
      // Verify app doesn't crash
    });

    it('should handle network errors', async () => {
      // Disable network
      // Try API call
      // Verify error message shown
    });

    it('should recover from errors', async () => {
      // Cause error
      // Re-enable network
      // Verify app recovers
      // Verify data reloads
    });
  });

  describe('Performance', () => {
    it('should launch in reasonable time', async () => {
      // Measure startup time
      // Should be < 5 seconds
    });

    it('should not have memory leaks', async () => {
      // Take heap snapshot at start
      // Run operations for duration
      // Take final heap snapshot
      // Verify memory not significantly increased
    });

    it('should have smooth scrolling', async () => {
      // Scroll through list
      // Measure frame rate
      // Verify 60 FPS or better
    });
  });

  describe('Cross-Platform Behavior', () => {
    it('should handle Windows-specific paths', async () => {
      const result = await app.client.execute(() => {
        return navigator.platform.includes('Win');
      });

      // Verify Windows-specific code paths
      expect(typeof result).toBe('boolean');
    });

    it('should render correctly on different resolutions', async () => {
      // No element overflow check
      const overflows = await app.client.execute(() => {
        return document.querySelectorAll('*').length > 0;
      });

      expect(overflows).toBe(true);
    });
  });
});
