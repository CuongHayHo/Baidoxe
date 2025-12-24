# Testing & QA Guide

## Overview

Desktop app testing bao gồm:
- Unit tests (React components, utilities)
- Integration tests (API, Electron IPC)
- E2E tests (User workflows)
- Manual testing checklist

## Testing Stack

- **Jest** - Unit testing framework
- **React Testing Library** - Component testing
- **Playwright/Spectron** - E2E testing
- **Mock Service Worker** - API mocking

## Setup

### Install Testing Dependencies

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest ts-jest
npm install --save-dev spectron @playwright/test
```

### Jest Configuration

Create `jest.config.js`:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts?(x)', '**/?(*.)+(spec|test).ts?(x)'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/main.js'
  ]
};
```

## Unit Tests

### React Component Example

```typescript
// src/components/__tests__/Dashboard.test.tsx

import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  it('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  });

  it('displays parking statistics', async () => {
    render(<Dashboard />);
    
    // Wait for data to load
    const stats = await screen.findByText(/Total Cards/i);
    expect(stats).toBeInTheDocument();
  });

  it('handles API errors gracefully', () => {
    // Mock API error
    // Verify error message shown
  });
});
```

### Hook Testing Example

```typescript
// src/__tests__/useElectron.test.ts

import { renderHook, act } from '@testing-library/react';
import useElectron from '../useElectron';

describe('useElectron Hook', () => {
  beforeEach(() => {
    // Mock window.electron
    global.window.electron = {
      isElectron: true,
      showNotification: jest.fn(),
      openFile: jest.fn(),
      // ... other mocks
    };
  });

  it('detects electron environment', () => {
    const { result } = renderHook(() => useElectron());
    expect(result.current.isElectron).toBe(true);
  });

  it('calls showNotification', async () => {
    const { result } = renderHook(() => useElectron());
    
    await act(async () => {
      await result.current.showNotification('Title', 'Body');
    });

    expect(window.electron.showNotification).toHaveBeenCalled();
  });

  it('handles non-electron environment', () => {
    delete global.window.electron;
    
    const { result } = renderHook(() => useElectron());
    expect(result.current.isElectron).toBe(false);
  });
});
```

## Integration Tests

### API Testing Example

```typescript
// src/api/__tests__/api.test.ts

import axios from 'axios';
import parkingApi from '../api';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Parking API', () => {
  it('fetches cards successfully', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: {
        cards: [
          { uid: '123', status: 0, created_at: '2025-01-01' }
        ],
        success: true
      }
    });

    const cards = await parkingApi.getCards();
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/cards/');
    expect(cards['123']).toBeDefined();
  });

  it('handles API errors', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

    await expect(parkingApi.getCards()).rejects.toThrow('Network error');
  });
});
```

### IPC Testing Example

```typescript
// Tests for Electron IPC handlers

describe('Electron IPC Handlers', () => {
  it('handles show-notification', async () => {
    // Mock ipcMain
    const notification = new Notification({
      title: 'Test',
      body: 'Test message'
    });

    // Verify notification shown
    expect(notification.title).toBe('Test');
  });

  it('opens file dialog', async () => {
    // Mock dialog.showOpenDialog
    // Test returns file path
  });

  it('gets backend status', async () => {
    // Mock axios GET request
    // Test returns true/false
  });
});
```

## E2E Tests

### Spectron (Electron E2E)

```typescript
// e2e/main.test.ts

import { Application } from 'spectron';
import * as path from 'path';

describe('Application', () => {
  let app: Application;

  beforeAll(() => {
    app = new Application({
      path: path.join(__dirname, '../dist/win-unpacked/Baidoxe.exe'),
      args: [],
    });
    return app.start();
  });

  afterAll(() => {
    if (app && app.isRunning()) {
      return app.stop();
    }
  });

  it('shows main window', async () => {
    const count = await app.client.getWindowCount();
    expect(count).toBe(1);
  });

  it('loads React app', async () => {
    const title = await app.client.getTitle();
    expect(title).toContain('Baidoxe');
  });

  it('displays dashboard', async () => {
    const dashboard = await app.client.$('div[role="main"]');
    expect(await dashboard.isDisplayed()).toBe(true);
  });

  it('navigates to cards tab', async () => {
    const cardsBtn = await app.client.$('[onclick*="cards"]');
    await cardsBtn.click();
    
    const cardsList = await app.client.$('div[class*="card-list"]');
    expect(await cardsList.isDisplayed()).toBe(true);
  });

  it('shows system tray icon', async () => {
    const trayIconCount = await app.client.execute(() => {
      // Check for tray icon
      return 1;
    });
    expect(trayIconCount).toBeGreaterThan(0);
  });

  it('backend communicates correctly', async () => {
    // Verify API calls work
    const response = await app.client.execute(async () => {
      return await window.electron.getBackendStatus();
    });
    expect(response).toBe(true);
  });
});
```

### Playwright (Alternative E2E)

```typescript
// e2e/ui.test.ts

import { test, expect } from '@playwright/test';

test.describe('Baidoxe Desktop', () => {
  test.beforeEach(async ({ page }) => {
    // Launch Electron with Playwright
    // await page.goto('app://');
  });

  test('displays main window', async ({ page }) => {
    const heading = page.locator('text=Baidoxe');
    await expect(heading).toBeVisible();
  });

  test('navigates between tabs', async ({ page }) => {
    // Click cards tab
    await page.click('button:has-text("Cards")');
    
    // Verify cards view loaded
    const cardsList = page.locator('[data-testid="cards-list"]');
    await expect(cardsList).toBeVisible();
  });

  test('shows/hides tray on minimize', async ({ page }) => {
    // Minimize window
    // Verify tray interaction works
  });

  test('exports data successfully', async ({ page }) => {
    // Click export button
    // Verify file saved
  });
});
```

## Running Tests

### Unit & Integration Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- Dashboard.test.tsx

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### E2E Tests

```bash
# Build first
npm run build

# Run Spectron tests
npm run test:e2e

# Run Playwright tests
npx playwright test
```

## Manual Testing Checklist

### Functionality
- [ ] App starts without errors
- [ ] Dashboard loads and displays stats
- [ ] Card operations (add/delete) work
- [ ] Parking slots update correctly
- [ ] Logs display properly
- [ ] Admin functions (backup/restore) work
- [ ] Export/import data works

### Native Features
- [ ] Notifications display
- [ ] File dialogs work
- [ ] Data export creates valid JSON
- [ ] System tray responds to clicks
- [ ] Context menu works

### Backend Integration
- [ ] Backend starts automatically
- [ ] API calls succeed
- [ ] Fallback URLs work if localhost fails
- [ ] Error handling shows proper messages
- [ ] Backend can be controlled from app

### Cross-Platform
- [ ] Windows: Installer works, tray works, shortcuts work
- [ ] macOS: DMG installs, app launch works, menu bar works
- [ ] Linux: AppImage works, install instructions clear

### Performance
- [ ] App launches in < 5 seconds
- [ ] Smooth scrolling in lists
- [ ] No memory leaks (check after 1 hour)
- [ ] CPU usage stays low when idle

### Edge Cases
- [ ] Backend fails to start gracefully
- [ ] No backend connection shows error
- [ ] Large data sets handled (1000+ cards)
- [ ] Rapid operations don't cause issues
- [ ] Network disconnection handled

## CI/CD Testing

### GitHub Actions Example

```yaml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '16'

      - run: cd desktop && npm install
      - run: cd desktop && npm test
      - run: cd desktop && npm run build
```

## Performance Profiling

### Check Memory Usage

```bash
# Run app and monitor
npm run dev

# In DevTools:
# - Performance tab
# - Memory tab
# - Take heap snapshots
```

### Check Startup Time

```bash
# Measure time to ready
time npm run electron-dev
```

## Debugging Tests

### Debug Jest Tests

```bash
node --inspect-brk ./node_modules/.bin/jest --runInBand
```

### Debug E2E Tests

```bash
PWDEBUG=1 npx playwright test
```

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Mocking** - Mock external dependencies (API, IPC)
3. **Async Handling** - Use async/await properly
4. **Cleanup** - Clean up after tests
5. **Meaningful Names** - Clear test descriptions
6. **Fast Execution** - Keep tests quick
7. **Coverage** - Aim for 70%+ coverage
8. **E2E Sparingly** - Use E2E for critical paths only

## Troubleshooting

### Tests timing out

```javascript
jest.setTimeout(10000); // Increase timeout
```

### Electron window not found in tests

```typescript
// Wait for window to be ready
await app.client.waitUntilWindowLoaded();
```

### API mocks not working

```javascript
// Ensure mock is set before import
jest.mock('axios');
import parkingApi from './api';
```
