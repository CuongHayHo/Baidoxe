/**
 * App_Router.tsx - Component chính với React Router
 * Mỗi trang có URL riêng: /dashboard, /cards, /parking, /logs, /admin
 */

import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ParkingCard } from './types';
import { parkingApi } from './api';
import CardList from './components/CardList';
import AddCardForm from './components/AddCardForm';
import UnknownCardNotification from './components/UnknownCardNotification';
import ParkingSlots from './components/ParkingSlots';
import Dashboard from './components/Dashboard';
import LogViewer from './components/LogViewer';
import AdminPanel from './components/AdminPanel';
import { NotificationProvider, useActivityMonitor, useStatsMonitor } from './components/Notifications';
import './App.css';

// ================== SHARED LAYOUT COMPONENT ==================
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  
  // ================== SHARED STATE ==================
  const [cards, setCards] = useState<Record<string, ParkingCard>>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [unknownCards, setUnknownCards] = useState<any[]>([]);

  // ================== SHARED API FUNCTIONS ==================
  const fetchCards = useCallback(async () => {
    try {
      const data = await parkingApi.getCards();
      setCards(data);
      setMessage('');
    } catch (error) {
      console.error('Failed to fetch cards:', error);
      setMessage('❌ Lỗi kết nối API server');
    }
  }, []);

  const fetchUnknownCards = useCallback(async () => {
    try {
      const data = await parkingApi.getUnknownCards();
      setUnknownCards(data);
    } catch (error) {
      console.error('Failed to fetch unknown cards:', error);
    }
  }, []);

  const handleAddCard = async (uid: string, status: number) => {
    setLoading(true);
    try {
      const success = await parkingApi.addCard(uid, status);
      if (success) {
        setMessage(`✅ Đã thêm thẻ ${uid}`);
        fetchCards();
      } else {
        setMessage(`❌ Không thể thêm thẻ ${uid}`);
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        setMessage(`⚠️ Thẻ ${uid} đã tồn tại`);
      } else {
        setMessage(`❌ Lỗi thêm thẻ: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCard = async (uid: string) => {
    if (!window.confirm(`Xóa thẻ ${uid}?`)) return;
    
    setLoading(true);
    try {
      const success = await parkingApi.deleteCard(uid);
      if (success) {
        setMessage(`✅ Đã xóa thẻ ${uid}`);
        fetchCards();
      } else {
        setMessage(`❌ Không thể xóa thẻ ${uid}`);
      }
    } catch (error: any) {
      setMessage(`❌ Lỗi xóa thẻ: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReload = async () => {
    setLoading(true);
    try {
      const message = await parkingApi.reload();
      setMessage(`🔄 ${message}`);
      fetchCards();
    } catch (error: any) {
      setMessage(`❌ Lỗi reload: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ================== EFFECTS ==================
  useEffect(() => {
    let title = '🅿️ Bãi đỗ xe thông minh';
    
    switch (location.pathname) {
      case '/':
      case '/dashboard':
        title = '📊 Dashboard - Bãi đỗ xe thông minh';
        break;
      case '/cards':
        title = '⏱️ Quản lý thẻ - Bãi đỗ xe thông minh';
        break;
      case '/parking':
        title = '🅿️ Vị trí đỗ xe - Bãi đỗ xe thông minh';
        break;
      case '/logs':
        title = '📋 Nhật ký - Bãi đỗ xe thông minh';
        break;
      case '/admin':
        title = '🔧 Quản trị - Bãi đỗ xe thông minh';
        break;
    }
    
    document.title = title;
  }, [location.pathname]);

  // Fetch data for cards page
  useEffect(() => {
    if (location.pathname === '/cards') {
      const fetchData = () => {
        fetchCards();
        fetchUnknownCards();
      };
      
      fetchData();
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [location.pathname, fetchCards, fetchUnknownCards]);

  // Auto-clear message
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  // ================== BREADCRUMB ==================
  const getBreadcrumb = () => {
    switch (location.pathname) {
      case '/':
      case '/dashboard':
        return '📊 Dashboard';
      case '/cards':
        return '⏱️ Quản lý thẻ';
      case '/parking':
        return '🅿️ Vị trí đỗ xe';
      case '/logs':
        return '📋 Nhật ký';
      case '/admin':
        return '🔧 Quản trị';
      default:
        return '📊 Dashboard';
    }
  };

  // ================== STATISTICS ==================
  const insideCount = Object.values(cards).filter(card => 
    card && typeof card === 'object' && 'status' in card && (card as ParkingCard).status === 1
  ).length;
  const totalCount = Object.keys(cards).length;

  // ================== SHARED PROPS ==================
  const sharedProps = {
    cards,
    loading,
    message,
    unknownCards,
    handleAddCard,
    handleDeleteCard,
    handleReload,
    fetchCards,
    fetchUnknownCards
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="App-header">
        <h1>🅿️ Hệ thống quản lý bãi đỗ xe</h1>
        
        {/* Page breadcrumb */}
        <div className="breadcrumb">
          <Link to="/" className="breadcrumb-home">🏠 Trang chủ</Link>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">{getBreadcrumb()}</span>
        </div>

        {/* Navigation */}
        <div className="navigation">
          <div className="nav-buttons">
            <Link 
              to="/dashboard" 
              className={`nav-button ${location.pathname === '/dashboard' || location.pathname === '/' ? 'active' : ''}`}
            >
              📊 Dashboard
            </Link>
            <Link 
              to="/cards" 
              className={`nav-button ${location.pathname === '/cards' ? 'active' : ''}`}
            >
              ⏱️ Quản lý thẻ
            </Link>
            <Link 
              to="/parking" 
              className={`nav-button ${location.pathname === '/parking' ? 'active' : ''}`}
            >
              🅿️ Vị trí đỗ xe
            </Link>
            <Link 
              to="/logs" 
              className={`nav-button ${location.pathname === '/logs' ? 'active' : ''}`}
            >
              📋 Nhật ký
            </Link>
            <Link 
              to="/admin" 
              className={`nav-button ${location.pathname === '/admin' ? 'active' : ''}`}
            >
              ⚙️ Quản trị
            </Link>
          </div>
        </div>
        
        {/* Statistics */}
        <div className="stats">
          <span className="stat">📊 Tổng: {totalCount}</span>
          <span className="stat">🅿️ Trong bãi: {insideCount}</span>
          <span className="stat">🚗 Ngoài bãi: {totalCount - insideCount}</span>
        </div>
      </header>

      {/* Messages */}
      {message && <div className="message">{message}</div>}
      {loading && <div className="loading">⏳ Đang xử lý...</div>}

      {/* Page Content */}
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route 
          path="/cards" 
          element={
            <CardsPage 
              cards={sharedProps.cards}
              unknownCards={sharedProps.unknownCards}
              handleAddCard={sharedProps.handleAddCard}
              handleDeleteCard={sharedProps.handleDeleteCard}
              handleReload={sharedProps.handleReload}
              fetchCards={sharedProps.fetchCards}
              fetchUnknownCards={sharedProps.fetchUnknownCards}
              loading={sharedProps.loading}
            />
          } 
        />
        <Route path="/parking" element={<ParkingSlots onBack={() => window.history.back()} />} />
        <Route path="/logs" element={<LogViewer />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>

      {/* Footer */}
      <footer className="App-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>🚗 Hệ thống BaiDoXe</h3>
            <p>Giải pháp quản lý bãi đỗ xe thông minh với RFID và IoT</p>
          </div>
          <div className="footer-section">
            <h3>📊 Thống kê nhanh</h3>
            <div className="footer-stats">
              <div className="stat-item">
                <span className="stat-label">🎯 Tổng thẻ</span>
                <span className="stat-value">{totalCount}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">🅿️ Trong bãi</span>
                <span className="stat-value">{insideCount}</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

// ================== CARDS PAGE COMPONENT ==================
const CardsPage: React.FC<{
  cards: Record<string, ParkingCard>;
  unknownCards: any[];
  handleAddCard: (uid: string, status: number) => Promise<void>;
  handleDeleteCard: (uid: string) => Promise<void>;
  handleReload: () => Promise<void>;
  fetchCards: () => Promise<void>;
  fetchUnknownCards: () => Promise<void>;
  loading: boolean;
}> = ({ cards, unknownCards, handleAddCard, handleDeleteCard, handleReload, fetchCards, loading }) => {
  return (
    <>
      <UnknownCardNotification 
        unknownCards={unknownCards}
        onAddCard={handleAddCard}
        onRefresh={fetchCards}
      />

      <main className="App-main">
        <div className="controls">
          <button onClick={fetchCards} disabled={loading}>
            🔄 Làm mới
          </button>
          <button onClick={handleReload} disabled={loading}>
            📁 Reload từ file
          </button>
        </div>

        <div className="content">
          <div className="left-panel">
            <AddCardForm onAddCard={handleAddCard} />
          </div>
          <div className="right-panel">
            <CardList cards={cards} onDeleteCard={handleDeleteCard} />
          </div>
        </div>
      </main>
    </>
  );
};

// ================== MAIN APP COMPONENT ==================
const App: React.FC = () => {
  return (
    <NotificationProvider>
      <Router>
        <AppWithHooks />
      </Router>
    </NotificationProvider>
  );
};

const AppWithHooks: React.FC = () => {
  useActivityMonitor();
  useStatsMonitor();
  
  return (
    <Layout>
      <div />
    </Layout>
  );
};

export default App;