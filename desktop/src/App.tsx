/**
 * App.tsx - Main app component cho Electron desktop app
 * Tái sử dụng React components từ frontend
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import './components/App.css';
import './components/index.css';

// Import existing components từ local src/components
import Dashboard from './components/Dashboard';
import CardList from './components/CardList';
import ParkingSlots from './components/ParkingSlots';
import AdminPanel from './components/AdminPanel';
import LogViewer from './components/LogViewer';
import { NotificationProvider } from './components/Notifications';

type Tab = 'dashboard' | 'cards' | 'parking' | 'logs' | 'admin';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [backendStatus, setBackendStatus] = useState(false);
  const [cards, setCards] = useState<Record<string, any>>({});

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
        return <CardList cards={cards} onDeleteCard={(uid: string) => {
          const newCards = { ...cards };
          delete newCards[uid];
          setCards(newCards);
        }} />;
      case 'parking':
        return <ParkingSlots onBack={() => setActiveTab('dashboard')} />;
      case 'logs':
        return <LogViewer />;
      case 'admin':
        return <AdminPanel />;
      default:
        return <Dashboard />;
    }
  };

  // Get breadcrumb text
  const getBreadcrumbText = () => {
    switch (activeTab) {
      case 'dashboard': return '📊 Dashboard';
      case 'cards': return '🎫 Quản lý thẻ';
      case 'parking': return '🅿️ Bãi xe';
      case 'logs': return '📝 Logs';
      case 'admin': return '⚙️ Quản trị';
      default: return '📊 Dashboard';
    }
  };

  // Calculate stats from cards
  const totalCards = Object.keys(cards).length;
  const insideCards = Object.values(cards).filter((c: any) => c?.status === 1).length;
  const outsideCards = totalCards - insideCards;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="App-header">
        <h1>🅿️ Hệ thống quản lý bãi đỗ xe</h1>
        
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <span className="breadcrumb-home">🏠 Trang chủ</span>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">{getBreadcrumbText()}</span>
        </div>

        {/* Stats */}
        <div className="stats">
          <span className="stat">📊 Tổng: {totalCards}</span>
          <span className="stat">🅿️ Trong bãi: {insideCards}</span>
          <span className="stat">🚗 Ngoài bãi: {outsideCards}</span>
        </div>

        {/* Navigation buttons */}
        <div className="navigation">
          <div className="nav-buttons">
            <button 
              className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dashboard
            </button>
            <button 
              className={`nav-button ${activeTab === 'cards' ? 'active' : ''}`}
              onClick={() => setActiveTab('cards')}
            >
              🎫 Quản lý thẻ
            </button>
            <button 
              className={`nav-button ${activeTab === 'parking' ? 'active' : ''}`}
              onClick={() => setActiveTab('parking')}
            >
              🅿️ Vị trí đỗ xe
            </button>
            <button 
              className={`nav-button ${activeTab === 'logs' ? 'active' : ''}`}
              onClick={() => setActiveTab('logs')}
            >
              📝 Nhật ký
            </button>
            <button 
              className={`nav-button ${activeTab === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveTab('admin')}
            >
              ⚙️ Quản trị
            </button>
          </div>
          <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
            {backendStatus ? '🟢 Online' : '🔴 Offline'}
          </span>
        </div>
      </header>

      <main className="app-content">{renderContent()}</main>
    </div>
  );
}

export default App;
