/**
 * App.tsx - Main app component với Authentication
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import './components/App.css';
import './components/index.css';
import './styles/AdminPanel.css';
import './styles/UserManagement.css';
import './styles/LoginPage.css';

// Import components
import Dashboard from './components/Dashboard';
import CardList from './components/CardList';
import ParkingSlots from './components/ParkingSlots';
import AdminPanel from './components/AdminPanel';
import LogViewer from './components/LogViewer';
import LoginPage from './components/LoginPage';
import { NotificationProvider, useActivityMonitor, useStatsMonitor } from './components/Notifications';

type Tab = 'dashboard' | 'cards' | 'parking' | 'logs' | 'admin';

// ============ Main App Component ============
const AppContent: React.FC<{ onLogout: () => void; userRole?: string }> = ({ onLogout, userRole = 'user' }) => {
  // Gọi activity monitor hooks để theo dõi logs mới từ UNO R4
  useActivityMonitor();
  useStatsMonitor();

  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [backendStatus, setBackendStatus] = useState(false);
  const [cards, setCards] = useState<Record<string, any>>({});

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
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch cards from API
  useEffect(() => {
    const fetchCards = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) return;
        
        const response = await fetch('http://localhost:5000/api/cards/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.cards && Array.isArray(data.cards)) {
            // Convert array to object format (key = uid)
            const cardsObj = data.cards.reduce((acc: any, card: any) => {
              acc[card.uid] = {
                status: card.status,
                parking_duration: card.parking_duration,
                created_at: card.created_at,
                entry_time: card.entry_time,
                exit_time: card.exit_time,
                name: card.name
              };
              return acc;
            }, {});
            setCards(cardsObj);
          }
        }
      } catch (error) {
        console.error('Error fetching cards:', error);
      }
    };

    fetchCards();
    const interval = setInterval(fetchCards, 5000); // Refresh mỗi 5 giây
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
        if (userRole === 'admin') {
          return <AdminPanel />;
        } else {
          return <Dashboard />;
        }
      default:
        return <Dashboard />;
    }
  };

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

  const totalCards = Object.keys(cards).length;
  const insideCards = Object.values(cards).filter((c: any) => c?.status === 1).length;
  const outsideCards = totalCards - insideCards;

  return (
    <div className="app-container">
      <header className="App-header">
        <h1>🅿️ Hệ thống quản lý bãi đỗ xe</h1>
        
        <div className="breadcrumb">
          <span className="breadcrumb-home">🏠 Trang chủ</span>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">{getBreadcrumbText()}</span>
        </div>

        <div className="stats">
          <span className="stat">📊 Tổng: {totalCards}</span>
          <span className="stat">🅿️ Trong bãi: {insideCards}</span>
          <span className="stat">🚗 Ngoài bãi: {outsideCards}</span>
        </div>

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
              disabled={userRole !== 'admin'}
              style={{ 
                opacity: userRole === 'admin' ? 1 : 0.3,
                cursor: userRole === 'admin' ? 'pointer' : 'not-allowed'
              }}
              title={userRole !== 'admin' ? 'Chỉ quản trị viên có thể truy cập' : ''}
            >
              ⚙️ Quản trị
            </button>
            <button 
              className="nav-button logout-btn"
              onClick={onLogout}
            >
              🚪 Đăng xuất
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
};

// ============ App with Authentication ============
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [userRole, setUserRole] = useState<string>('user');

  useEffect(() => {
    console.log('🔍 App component MOUNTED - checking token...');
    verifyToken();
  }, []);

  const verifyToken = async () => {
    try {
      const token = localStorage.getItem('authToken');
      console.log('📌 Token in localStorage:', token ? 'EXISTS' : 'MISSING');

      if (!token) {
        console.log('❌ No token found - show LoginPage');
        setIsLoggedIn(false);
        setIsChecking(false);
        return;
      }

      // Verify token with backend
      const response = await fetch('http://localhost:5000/api/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Verify response:', response.status);

      if (response.ok) {
        console.log('✅ Token valid - SHOW DASHBOARD');
        const savedRole = localStorage.getItem('userRole') || 'user';
        setUserRole(savedRole);
        setIsLoggedIn(true);
      } else {
        console.log('❌ Token invalid - CLEAR AND SHOW LOGIN');
        localStorage.removeItem('authToken');
        setIsLoggedIn(false);
      }
    } catch (error) {
      console.error('🔴 Verification error:', error);
      localStorage.removeItem('authToken');
      setIsLoggedIn(false);
    } finally {
      setIsChecking(false);
    }
  };

  const handleLogin = (token: string, role?: string) => {
    console.log('✅ LOGIN SUCCESS - storing token and showing dashboard');
    localStorage.setItem('authToken', token);
    if (role) {
      localStorage.setItem('userRole', role);
      setUserRole(role);
    }
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    console.log('🚪 LOGOUT - clearing token and showing login');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    setUserRole('user');
    setIsLoggedIn(false);
  };

  if (isChecking) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f0f0f0',
        fontSize: '24px'
      }}>
        ⏳ Đang kiểm tra đăng nhập...
      </div>
    );
  }

  return (
    <NotificationProvider>
      {isLoggedIn ? (
        <AppContent onLogout={handleLogout} userRole={userRole} />
      ) : (
        <LoginPage onLoginSuccess={handleLogin} />
      )}
    </NotificationProvider>
  );
}

export default App;
