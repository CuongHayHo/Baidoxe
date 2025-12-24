/**
 * App.tsx - Main app component cho Electron desktop app
 * Tái sử dụng React components từ frontend
 */

import React, { useState, useEffect } from 'react';
import './App.css';

// Import existing components từ frontend
import Dashboard from '../../frontend/src/components/Dashboard';
import CardList from '../../frontend/src/components/CardList';
import ParkingSlots from '../../frontend/src/components/ParkingSlots';
import AdminPanel from '../../frontend/src/components/AdminPanel';
import LogViewer from '../../frontend/src/components/LogViewer';
import { NotificationProvider } from '../../frontend/src/components/Notifications';

type Tab = 'dashboard' | 'cards' | 'parking' | 'logs' | 'admin';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [backendStatus, setBackendStatus] = useState(false);

  // Check backend status on mount
  useEffect(() => {
    const checkBackend = async () => {
      if (window.electron) {
        try {
          const status = await window.electron.getBackendStatus();
          setBackendStatus(status);
        } catch (error) {
          console.error('Failed to check backend:', error);
          setBackendStatus(false);
        }
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 10000); // Check every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'cards':
        return <CardList />;
      case 'parking':
        return <ParkingSlots />;
      case 'logs':
        return <LogViewer />;
      case 'admin':
        return <AdminPanel />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <nav className="desktop-navbar">
        <div className="nav-brand">
          <span className="brand-icon">🅿️</span>
          <span className="brand-name">Baidoxe Desktop</span>
        </div>

        <ul className="nav-menu">
          <li>
            <button
              className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dashboard
            </button>
          </li>
          <li>
            <button
              className={`nav-btn ${activeTab === 'cards' ? 'active' : ''}`}
              onClick={() => setActiveTab('cards')}
            >
              🎫 Thẻ xe
            </button>
          </li>
          <li>
            <button
              className={`nav-btn ${activeTab === 'parking' ? 'active' : ''}`}
              onClick={() => setActiveTab('parking')}
            >
              🅿️ Bãi xe
            </button>
          </li>
          <li>
            <button
              className={`nav-btn ${activeTab === 'logs' ? 'active' : ''}`}
              onClick={() => setActiveTab('logs')}
            >
              📝 Logs
            </button>
          </li>
          <li>
            <button
              className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveTab('admin')}
            >
              ⚙️ Quản trị
            </button>
          </li>
        </ul>

        <div className="nav-status">
          <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
            {backendStatus ? '🟢 Online' : '🔴 Offline'}
          </span>
        </div>
      </nav>

      <main className="app-content">{renderContent()}</main>
    </div>
  );
}

export default App;
