# 🔧 Kiến Trúc Kỹ Thuật & Giải Thích Code - Hệ Thống Bãi Đỗ Xe Thông Minh

> **📝 Lưu ý về Code Examples**: Tài liệu này chứa các đoạn code được trích xuất trực tiếp từ files nguồn thực tế của dự án. Một số đoạn code có thể được rút gọn để tập trung vào các khái niệm chính, nhưng đã được cập nhật để phản ánh chính xác cấu trúc và logic thực tế của hệ thống.

## 📋 Tổng Quan Kiến Trúc

Hệ thống được xây dựng theo **kiến trúc phân lớp (Layered Architecture)** với **mô hình Client-Server**:

### **🏗️ Các lớp kiến trúc từ trên xuống:**

1. **🌐 LỚP GIAO DIỆN NGƯỜI DÙNG (Presentation Layer)**
   - **Công nghệ**: React TypeScript
   - **Chức năng**: Hiển thị giao diện web, xử lý tương tác người dùng
   - **Giao tiếp**: HTTP API calls tới lớp Logic Nghiệp Vụ

2. **⚙️ LỚP LOGIC NGHIỆP VỤ (Business Logic Layer)**  
   - **Công nghệ**: Python Flask Server
   - **Chức năng**: Xử lý business rules, API endpoints, validation
   - **Giao tiếp**: Nhận HTTP requests từ frontend, thao tác file với Data Layer

3. **💿 LỚP TRUY CẬP DỮ LIỆU (Data Access Layer)**
   - **Công nghệ**: JSON Files + Backup System  
   - **Chức năng**: Lưu trữ dữ liệu thẻ, logs, backup/restore
   - **Giao tiếp**: File I/O operations, được truy cập bởi Business Layer

4. **🔌 LỚP PHẦN CỨNG (Hardware Layer)**
   - **Công nghệ**: Arduino UNO R4 WiFi + ESP32 + RFID Sensors
   - **Chức năng**: Đọc thẻ RFID, điều khiển barriers, phát hiện xe đỗ
   - **Giao tiếp**: HTTP requests tới Backend, WiFi communication


---

## 🎯 Công Nghệ Sử Dụng

### 💻 **Giao Diện Người Dùng (Frontend)**
- **React 18**: Framework JavaScript để xây dựng giao diện
- **TypeScript**: Ngôn ngữ lập trình có kiểm tra kiểu dữ liệu
- **React Router**: Quản lý điều hướng trang (URL routing)
- **Axios**: Thư viện giao tiếp với API server
- **CSS3**: Styling và responsive design

### ⚙️ **Máy Chủ Xử Lý (Backend)**
- **Python 3.8+**: Ngôn ngữ lập trình chính
- **Flask**: Web framework nhẹ để tạo API server
- **Flask-CORS**: Xử lý Cross-Origin Resource Sharing
- **JSON**: Định dạng lưu trữ dữ liệu
- **Threading**: Xử lý đa luồng cho scheduled tasks

### 🔌 **Hardware (Phần Cứng)**
- **Arduino UNO R4 WiFi**: Vi điều khiển chính đọc RFID
- **ESP32**: Vi điều khiển phụ với cảm biến siêu âm
- **RFID RC522**: Module đọc thẻ từ
- **Ultrasonic Sensors**: Cảm biến khoảng cách HC-SR05

---

## 📁 Cấu Trúc Thư Mục Project


Baidoxe/
├── 🌐 frontend/                 # Giao diện web (React)
│   ├── src/
│   │   ├── components/          # Các component UI
│   │   ├── types.ts            # Định nghĩa kiểu dữ liệu
│   │   ├── api.ts              # Kết nối với máy chủ
│   │   └── App.tsx             # Component chính
│   ├── public/                 # Static files
│   └── build/                  # Code đã compile
│
├── ⚙️ backend/                  # Máy chủ xử lý (Python)
│   ├── api/                    # API endpoints
│   ├── services/               # Business logic
│   ├── models/                 # Data models
│   ├── utils/                  # Utilities
│   ├── config/                 # Cấu hình
│   └── data/                   # Dữ liệu JSON
│
├── 🔌 hardware/                 # Code cho vi điều khiển
│   ├── esp32_sensors/          # Code ESP32
│   └── uno_r4_wifi/            # Code Arduino UNO R4
│
├── 📋 scripts/                  # Scripts tiện ích
└── 📖 docs/                     # Tài liệu hướng dẫn


---

## 🌐 Giao diện người dùng (React) - Giải thích chi tiết

### 📱 **React TypeScript Frontend**

React là **thư viện JavaScript** để xây dựng giao diện người dùng động. Project này sử dụng **React + TypeScript** cho type safety và **React Router** cho navigation giữa các trang.

### 🧩 **Components Chính**

#### 1. **App.tsx - React Router & Shared State Management**

📁 **File: `frontend/src/App.tsx`**

```typescript
/**
 * App.tsx - Component chính với React Router và quản lý state toàn cục
 * 
 * KIẾN TRÚC:
 * - BrowserRouter: Quản lý URL routing cho SPA
 * - Layout Component: Shared UI shell với navigation và state
 * - Nested Routes: Mỗi trang có URL riêng (/dashboard, /cards, /parking, /logs, /admin)
 * - Centralized State: Cards, loading, messages được quản lý tập trung
 * 
 * PATTERN SỬ DỤNG: Layout-as-State-Container
 * Lý do: State cần được share giữa nhiều pages khác nhau
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
        
        {/* Navigation */}
        <div className="navigation">
          <div className="nav-buttons">
            <Link to="/dashboard" className={`nav-button ${location.pathname === '/dashboard' || location.pathname === '/' ? 'active' : ''}`}>
              📊 Dashboard
            </Link>
            <Link to="/cards" className={`nav-button ${location.pathname === '/cards' ? 'active' : ''}`}>
              ⏱️ Quản lý thẻ
            </Link>
            <Link to="/parking" className={`nav-button ${location.pathname === '/parking' ? 'active' : ''}`}>
              🅿️ Vị trí đỗ xe
            </Link>
            <Link to="/logs" className={`nav-button ${location.pathname === '/logs' ? 'active' : ''}`}>
              📋 Nhật ký
            </Link>
            <Link to="/admin" className={`nav-button ${location.pathname === '/admin' ? 'active' : ''}`}>
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
      {children}
    </div>
  );
};

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
        <Route path="/parking" element={<ParkingSlots />} />
        <Route path="/logs" element={<LogViewer />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Layout>
  );
};

export default App;
```

**🔧 Giải thích chi tiết App.tsx Architecture:**

**1. React Router Pattern:**
- **BrowserRouter**: Sử dụng HTML5 History API để điều hướng SPA
- **Nested Routes**: Mỗi trang có URL riêng biệt, hỗ trợ deep linking
- **Navigate component**: Tự động redirect từ "/" về "/dashboard"

**2. State Management Strategy:**
- **Centralized trong Layout**: Tất cả shared state (cards, loading, message) được quản lý ở Layout component
- **Props drilling**: Truyền state và functions xuống child components qua props
- **useCallback optimization**: Ngăn re-render không cần thiết của child components

**3. Component Composition:**
- **Layout Component**: UI shell chứa header, navigation, shared state
- **Page Components**: Dashboard, CardList, ParkingSlots, LogViewer, AdminPanel
- **NotificationProvider**: Context để quản lý notifications toàn cục

**4. Hooks Usage:**
- **useState**: Quản lý local state (cards, loading, message, unknownCards)
- **useEffect**: Auto page title update, data fetching lifecycle
- **useCallback**: Memoize functions để tối ưu performance

#### 2. **Dashboard.tsx - Trang Chủ**

📁 **File: `frontend/src/components/Dashboard.tsx`**

```typescript
/**
 * Dashboard Component - Trang chủ hiển thị thống kê tổng quan hệ thống
 * 
 * Chức năng chính:
 * - Hiển thị thống kê số lượng thẻ, xe trong/ngoài bãi
 * - Tỷ lệ sử dụng bãi xe với thanh progress bar
 * - Danh sách hoạt động gần đây (10 log mới nhất)
 * - Các thao tác nhanh: backup dữ liệu, sửa lỗi dữ liệu
 * - Tự động refresh mỗi 30 giây
 */

import React, { useState, useEffect } from 'react';

/**
 * Interface định nghĩa cấu trúc dữ liệu thống kê dashboard
 * - total_cards: Tổng số thẻ trong hệ thống
 * - inside_parking: Số xe đang trong bãi
 * - outside_parking: Số xe đang ở ngoài bãi  
 * - occupancy_rate: Tỷ lệ sử dụng bãi xe (%)
 */
interface DashboardStats {
  total_cards: number;
  inside_parking: number;
  outside_parking: number;
  occupancy_rate: number;
}

const Dashboard: React.FC = () => {
  // Lưu trữ dữ liệu thống kê từ API
  const [stats, setStats] = useState<DashboardStats | null>(null);
  // Lưu trữ danh sách log hoạt động gần đây
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  // Trạng thái loading khi đang fetch dữ liệu
  const [isLoading, setIsLoading] = useState(true);
  // Lưu trữ thông báo lỗi nếu có
  const [error, setError] = useState<string | null>(null);
  // Thời gian cập nhật cuối cùng để hiển thị cho user
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  /**
   * Hàm fetch dữ liệu dashboard từ API
   * - Gọi đồng thời 2 API: thống kê và log gần đây
   * - Xử lý lỗi và cập nhật state tương ứng
   * - Cập nhật thời gian fetch cuối cùng
   */
  const fetchStats = async () => {
    try {
      // Gọi đồng thời 2 API để tối ưu tốc độ loading
      const [statsResponse, logsResponse] = await Promise.all([
        fetch('/api/cards/statistics'),    // API lấy thống kê tổng quan
        fetch('/api/cards/logs?limit=10')  // API lấy 10 log gần đây nhất
      ]);

      // Xử lý response API thống kê
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        // Support cả 2 format response: {statistics: {...}} và {...}
        setStats(statsData.statistics || statsData);
      }

      // Xử lý response API log hoạt động
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setRecentLogs(logsData);
      }

      // Cập nhật thời gian fetch thành công
      setLastUpdate(new Date());
      setError(null); // Clear lỗi cũ nếu có
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      // Luôn tắt loading dù thành công hay thất bại
      setIsLoading(false);
    }
  };

  /**
   * useEffect Hook - Xử lý lifecycle component
   * - Fetch dữ liệu lần đầu khi component mount
   * - Thiết lập auto-refresh mỗi 30 giây
   * - Cleanup interval khi component unmount
   */
  useEffect(() => {
    fetchStats(); // Fetch dữ liệu ngay khi component được render
    
    // Thiết lập auto refresh mỗi 30 giây để cập nhật real-time
    const interval = setInterval(fetchStats, 30000);
    
    // Cleanup function - xóa interval khi component unmount
    return () => clearInterval(interval);
  }, []); // Empty dependency array - chỉ chạy 1 lần khi mount

  // ... (continued - actual code có thêm nhiều functions và JSX render)
};

export default Dashboard;
```

**Giải thích Dashboard Component**:
- **Quản lý State**: Sử dụng `useState` để quản lý dữ liệu thống kê, logs, loading state
- **API Calls**: Dùng `fetch()` native để gọi 2 endpoints song song với `Promise.all`
- **Auto Refresh**: Tự động cập nhật dữ liệu mỗi 30 giây với `setInterval`
- **Error Handling**: Xử lý lỗi gracefully mà không crash application
- **TypeScript**: Type safety với interfaces cho data structures

> **📁 Full implementation**: Xem file `frontend/src/components/Dashboard.tsx` (359 dòng) với đầy đủ LogStats interface, các functions fetchStats, getActionColor, getActionIcon, formatTimestamp, và JSX render với stats grid, recent activity, quick actions.

**Giải thích Dashboard Component**:

**1. React Hooks được sử dụng**:
- `useState<T>`: Quản lý state cho thống kê, logs, loading và error
- `useEffect`: Tự động fetch dữ liệu khi component mount và thiết lập auto-refresh

**2. API Integration**:
- Sử dụng `fetch()` native để gọi REST API endpoints
- Gọi 2 API song song với `Promise.all` để tối ưu tốc độ
- Support error handling gracefully

**3. Real-time Features**:
- **Auto Refresh**: Tự động cập nhật dữ liệu mỗi 30 giây
- **Loading States**: Hiển thị spinner khi đang fetch dữ liệu  
- **Error Handling**: Hiển thị error message khi có lỗi API

**4. UI Components**:
- **Statistics Cards**: Hiển thị tổng số thẻ, xe trong/ngoài bãi, tỷ lệ sử dụng
- **Activity Feed**: Danh sách 10 hoạt động gần đây nhất
- **Progress Bar**: Thanh hiển thị tỷ lệ sử dụng bãi xe
#### 3. **api.ts - Kết Nối Máy Chủ**

📁 **File: `frontend/src/api.ts`**

```typescript
/**
 * API Client - Kết nối frontend với backend server
 * 
 * Chức năng chính:
 * - Smart detection để tự động phát hiện backend URL
 * - Fallback system khi connection thất bại
 * - Interceptors để log và retry requests
 * - Type-safe methods cho tất cả API endpoints
 */

import axios from 'axios';
import { ParkingCard, ApiResponse } from './types';

/**
 * Hàm thông minh để phát hiện URL backend
 * - Development: sử dụng localhost:5000
 * - Production: sử dụng cùng IP với frontend + port 5000
 */
const getApiBaseUrl = () => {
  // Kiểm tra nếu đang chạy development (localhost frontend)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000'; // Thử localhost trước
  }
  
  // Nếu truy cập qua IP mạng, sử dụng cùng IP cho backend
  return `http://${window.location.hostname}:5000`;
};

/**
 * Danh sách URL fallback khi URL chính thất bại
 * Thử theo thứ tự ưu tiên từ trên xuống
 */
const FALLBACK_URLS = [
  'http://192.168.4.3:5000',  // IP backend đã được detect
  'http://127.0.0.1:5000',    // Local loopback
  'http://localhost:5000'     // Local hostname
];

// URL backend được phát hiện tự động
const API_BASE_URL = getApiBaseUrl();

/**
 * Tạo axios instance với cấu hình cơ bản
 * - Timeout: 10 giây
 * - Content-Type: JSON
 * - BaseURL: Tự động detect
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor - Ghi log mọi request để debug
 */
api.interceptors.request.use(request => {
  console.log('🚀 API Request:', `${API_BASE_URL}${request.url}`, request.method?.toUpperCase());
  return request;
});

/**
 * Response Interceptor - Xử lý response và retry logic
 * - Log thành công/thất bại
 * - Tự động thử fallback URLs khi connection lỗi
 */
api.interceptors.response.use(
  response => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  async error => {
    console.error('❌ API Error:', error.config?.url, error.message);
    
    // Thử fallback URLs khi URL chính thất bại
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.log('🔄 Đang thử các URL fallback...');
      
      for (const fallbackUrl of FALLBACK_URLS) {
        if (fallbackUrl === API_BASE_URL) continue; // Bỏ qua nếu trùng với URL hiện tại
        
        try {
          console.log(`🧪 Đang thử: ${fallbackUrl}`);
          const retryResponse = await axios({
            ...error.config,
            baseURL: fallbackUrl
          });
          console.log(`✅ Fallback thành công: ${fallbackUrl}`);
          return retryResponse;
        } catch (fallbackError) {
          console.log(`❌ Fallback thất bại: ${fallbackUrl}`);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Client Object - Tập hợp tất cả methods để giao tiếp với backend
 * Mỗi method tương ứng với 1 endpoint và có error handling
 */
export const parkingApi = {
  /**
   * Lấy danh sách tất cả thẻ từ server
   * @returns Record object với key là UID thẻ
   */
  getCards: async (): Promise<Record<string, ParkingCard>> => {
    const response = await api.get<{success: boolean, cards: ParkingCard[], count: number}>('/api/cards');
    const cardsObject: Record<string, ParkingCard> = {};
    if (response.data.cards && Array.isArray(response.data.cards)) {
      response.data.cards.forEach(card => {
        cardsObject[card.uid] = card;
      });
    }
    return cardsObject;
  },

  /**
   * Thêm thẻ mới vào hệ thống
   * @param uid - ID duy nhất của thẻ
   * @param status - Trạng thái: 0=active, 1=parked  
   */
  addCard: async (uid: string, status: number = 0): Promise<boolean> => {
    const statusMap = { 0: 'active', 1: 'parked' };
    const apiStatus = statusMap[status as keyof typeof statusMap] || 'active';
    
    const response = await api.post<ApiResponse<any>>('/api/cards', {
      id: uid,
      name: `Thẻ ${uid}`,
      status: apiStatus,
    });
    return response.data.success === true;
  },

  // ... (12+ methods khác: deleteCard, reload, getUnknownCards, v.v.)
};

export default parkingApi;
```



**🔧 Giải thích API Client Architecture:**

**1. Smart URL Detection:**
- **Dynamic Backend Discovery**: Tự động phát hiện IP của backend dựa trên hostname của frontend
- **Environment Awareness**: Dev (localhost) vs Production (network IP) automatic detection
- **Fallback Strategy**: List các URL backup để thử khi URL chính fail

**2. Axios Configuration:**
- **Instance Pattern**: Tạo configured axios instance thay vì dùng global axios
- **Timeout Protection**: 10s timeout để tránh hanging requests
- **Default Headers**: Set JSON content-type cho tất cả requests

**3. Interceptors System:**
- **Request Logging**: Log tất cả outgoing requests để debug
- **Response Handling**: Centralized success/error logging
- **Retry Logic**: Automatic fallback URL retry khi network fail
- **Error Classification**: Phân loại các loại lỗi network khác nhau

**4. Type Safety:**
- **Generic Methods**: Type-safe API calls với TypeScript generics
- **Interface Integration**: Sử dụng ParkingCard và ApiResponse interfaces
- **Return Type Consistency**: Consistent return formats cho error handling

**5. API Methods Design:**
- **RESTful Pattern**: Theo chuẩn REST API (GET, POST, DELETE)
- **Data Transformation**: Convert API response thành frontend-friendly format
- **Error Propagation**: Meaningful error messages cho UI layer

**5. Separation of Concerns**:
- `parkingApi`: Xử lý business logic của thẻ đỗ xe - THỰC TẾ chỉ có parkingApi duy nhất trong hệ thống

### 🔄 **Luồng dữ liệu (Data Flow)**


Người dùng nhấn nút → Bộ xử lý sự kiện Component → Gọi API → Xử lý Backend → Phản hồi JSON → Cập nhật trạng thái UI → Render lại Component


**Ví dụ thực tế - Thêm thẻ mới:**
1. User nhập UID và nhấn "Thêm thẻ"
2. `AddCardForm` component bắt sự kiện submit
3. Gọi `parkingApi.addCard(uid, status)`
4. Gửi HTTP POST đến backend `/api/cards`
5. Backend xử lý và trả về response
6. Frontend nhận response và cập nhật UI
7. Hiển thị thông báo thành công/thất bại

---

## ⚙️ Máy chủ xử lý (Python Flask) - Giải thích chi tiết

### 🐍 **Python Flask Backend**

Flask là **web framework** cho Python, tạo RESTful API endpoints để xử lý requests từ frontend và hardware. Backend này implement **Service Layer Pattern** và **Repository Pattern** cho business logic.

### 🏗️ **Kiến Trúc Backend**

#### 1. **app.py - Application Factory**
```python
def create_app():
    app = Flask(__name__)           # Tạo Flask app
    init_cors(app)                  # Enable CORS
    register_blueprints(app)        # Đăng ký API routes
    setup_error_handlers(app)       # Xử lý lỗi
    return app

app = create_app()  # Tạo instance ứng dụng


**Chức năng**:
- Tạo và cấu hình Flask application
- Thiết lập CORS để frontend có thể gọi API
- Đăng ký các API endpoints
- Xử lý lỗi toàn cục

#### 2. **API Endpoints (api/cards.py)**

📁 **File: `backend/api/cards.py`**

```python
"""
Cards API - Endpoints for parking card management
Xử lý tất cả API endpoints liên quan đến thẻ xe
"""
from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
from datetime import datetime, timezone

from services.card_service import CardService
from utils.validation import ValidationHelper

logger = logging.getLogger(__name__)

# Create blueprint for cards API
cards_bp = Blueprint('cards', __name__, url_prefix='/api/cards')

# Initialize card service
card_service = CardService()

@cards_bp.route('/', methods=['GET'])
def get_all_cards():
    """Lấy tất cả thẻ đỗ xe trong hệ thống"""
    try:
        logger.info("API: Getting all cards")
        cards_dict = card_service.get_all_cards()
        cards_data = [card.to_dict() for card in cards_dict.values()]
        
        return jsonify({
            "success": True,
            "cards": cards_data,
            "count": len(cards_data),
            "message": "Cards retrieved successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error getting all cards: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/', methods=['POST'])
def create_card():
    """Create new parking card với full validation"""
    # Implementation: JSON validation, UID processing, card creation
    # Full code in backend/api/cards.py
    pass

@cards_bp.route('/<card_id>', methods=['GET', 'PUT', 'DELETE'])  
def card_operations(card_id):
    """CRUD operations cho individual cards"""
    # GET: lấy thông tin 1 thẻ, PUT: cập nhật, DELETE: xóa thẻ
    # Full code in backend/api/cards.py  
    pass
```

> **📁 Full API**: File `backend/api/cards.py` (989 dòng) với đầy đủ 15+ endpoints: `/statistics`, `/logs`, `/scan`, `/backup`, `/fix-data`, v.v.

**Giải thích**:
- `@app.route`: Decorator định nghĩa URL endpoint và HTTP method
- `request.get_json()`: Lấy dữ liệu JSON từ HTTP request
- `jsonify()`: Chuyển Python object thành JSON response
- Error handling với try/catch và HTTP status codes

#### 3. **Business Logic (services/card_service.py)**

📁 **File: `backend/services/card_service.py`**

```python
"""
Card Service - Lớp xử lý logic nghiệp vụ cho các thao tác với thẻ đỗ xe

Chức năng chính:
- CRUD operations cho parking cards
- Quản lý unknown cards (thẻ lạ)  
- Tính toán thống kê hệ thống
- Auto-backup sau các thay đổi
- Logging cho audit trail
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging

from models.card import ParkingCard
from utils.file_manager import FileManager
from config.config import CARDS_FILE, UNKNOWN_CARDS_FILE

logger = logging.getLogger(__name__)

class CardService:
    """
    Service class xử lý tất cả business logic liên quan đến parking cards
    
    Sử dụng lazy loading cho backup_service và log_service để tránh circular imports
    """
    def __init__(self):
        self.file_manager = FileManager()
        # Lazy loading để tránh circular import
        self._backup_service = None
        self._log_service = None
    
    @property 
    def backup_service(self):
        # Lazy loading pattern
        pass
```

```python
"""
Card Service - Lớp xử lý logic nghiệp vụ cho các thao tác với thẻ đỗ xe

Chức năng chính:
- CRUD operations cho parking cards
- Quản lý unknown cards (thẻ lạ)  
- Tính toán thống kê hệ thống
- Auto-backup sau các thay đổi
- Logging cho audit trail
- Validation và error handling
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging

from models.card import ParkingCard
from utils.file_manager import FileManager
from config.config import CARDS_FILE, UNKNOWN_CARDS_FILE

logger = logging.getLogger(__name__)

class CardService:
    """
    Service class xử lý tất cả business logic liên quan đến parking cards
    
    Sử dụng lazy loading cho backup_service và log_service để tránh circular imports
    """
    def __init__(self):
        self.file_manager = FileManager()
        # Lazy loading để tránh circular import
        self._backup_service = None
        self._log_service = None
        
    @property
    def backup_service(self):
        if self._backup_service is None:
            from services.backup_service import BackupService
            self._backup_service = BackupService()
        return self._backup_service
    
    @property 
    def log_service(self):
        if self._log_service is None:
            from services.card_log_service import CardLogService
            self._log_service = CardLogService()
        return self._log_service

    def get_all_cards(self) -> Dict[str, ParkingCard]:
        """Đọc tất cả thẻ từ file JSON"""
        try:
            success, raw_data = self.file_manager.read_json(CARDS_FILE, default_value={})
            if not success:
                return {}
            return self._parse_cards_from_dict(raw_data)
        except Exception as e:
            logger.error(f"Error reading cards: {e}")
            return {}

    def create_card(self, uid: str, status: int = 0) -> Tuple[bool, str, Optional[ParkingCard]]:
        """
        Tạo thẻ mới - ACTUAL implementation 
        
        Args:
            uid (str): UID của thẻ RFID
            status (int): Trạng thái (0=ngoài bãi, 1=trong bãi)
            
        Returns:
            Tuple[bool, str, Optional[ParkingCard]]: (success, message, card_object)
        """
        try:
            cards_dict = self.get_all_cards()
            if uid in cards_dict:
                error_msg = f"Thẻ {uid} đã tồn tại"
                return False, error_msg, None
            
            new_card = ParkingCard(uid=uid, status=status)
            cards_dict[uid] = new_card
            
            # Convert to dict format for JSON storage
            cards_data = {card_uid: card_obj.to_dict() for card_uid, card_obj in cards_dict.items()}
            
            success, message = self.file_manager.write_json(CARDS_FILE, cards_data, max_backups=5)
            
            if success:
                # Log the creation
                from services.card_log_service import LogAction
                self.log_service.add_log(uid, LogAction.CARD_CREATED, {"initial_status": status})
                
                return True, f"Thẻ {uid} đã được thêm thành công", new_card
            else:
                return False, f"Lỗi lưu thẻ {uid}", None
                
        except Exception as e:
            return False, f"Lỗi tạo thẻ {uid}: {str(e)}", None
```

> **📁 Full Service**: File `backend/services/card_service.py` (296 dòng) với đầy đủ methods: `delete_card()`, `get_statistics()`, `get_unknown_cards()`, v.v.

```python
    def get_all_cards(self) -> Dict[str, Dict[str, Any]]:
        """Lấy tất cả thẻ từ file JSON"""
        try:
            cards_data = self.file_manager.read_json(self.CARDS_FILE)
            if cards_data is None:
                logger.info("📄 File cards.json chưa tồn tại, tạo file mới")
                return {}
            return cards_data
        except Exception as e:
            logger.error(f"❌ Lỗi đọc file cards: {str(e)}")
            return {}
    
    def get_card(self, uid: str) -> Optional[ParkingCard]:
        """Lấy thông tin 1 thẻ cụ thể"""
        uid = self._normalize_uid(uid)
        cards = self.get_all_cards()
        
        if uid in cards:
            card_data = cards[uid]
            return ParkingCard.from_dict(card_data)
        return None
    
    def update_card_status(self, uid: str, new_status: int) -> Tuple[bool, str]:
        """
        Cập nhật trạng thái thẻ (vào/ra bãi)
        Đây là function quan trọng nhất - được gọi khi scan RFID
        """
        try:
            uid = self._normalize_uid(uid)
            logger.info(f"🔄 Cập nhật trạng thái thẻ {uid}: {new_status}")
            
            # 1. Lấy thông tin thẻ hiện tại
            card = self.get_card(uid)
            if not card:
                # Thẻ không có trong hệ thống - thêm vào unknown_cards
                self._add_to_unknown_cards(uid)
                return False, f"Thẻ {uid} không có trong hệ thống"
            
            # 2. Kiểm tra trạng thái có thay đổi không
            if card.status == new_status:
                action = "vào bãi" if new_status == 1 else "ra bãi"
                return False, f"Thẻ {uid} đã {action} từ trước"
            
            # 3. Validate business rules cho status change
            if not self._can_change_status(card, new_status):
                return False, "Không thể thay đổi trạng thái thẻ lúc này"
            
            # 4. Cập nhật trạng thái
            old_status = card.status
            card.update_status(new_status)
            
            # 5. Lưu vào file
            all_cards = self.get_all_cards()
            all_cards[uid] = card.to_dict()
            
            success, error_msg = self.file_manager.atomic_write_json(
                self.CARDS_FILE, 
                all_cards
            )
            
            if not success:
                return False, f"Lỗi lưu dữ liệu: {error_msg}"
            
            # 6. Ghi log chi tiết
            action = LogAction.ENTRY if new_status == 1 else LogAction.EXIT
            action_text = "vào bãi" if new_status == 1 else "ra bãi"
            
            self.log_service.add_log(
                card_id=uid,
                action=action,
                details=f"Chuyển từ trạng thái {old_status} sang {new_status}"
            )
            
            logger.info(f"✅ Cập nhật thẻ {uid} {action_text} thành công")
            return True, f"Thẻ {uid} {action_text} thành công"
            
        except Exception as e:
            logger.error(f"💥 Exception trong update_card_status: {str(e)}")
            return False, f"Lỗi hệ thống: {str(e)}"
    
    def delete_card(self, uid: str) -> Tuple[bool, str]:
        """Xóa thẻ khỏi hệ thống"""
        try:
            uid = self._normalize_uid(uid)
            
            all_cards = self.get_all_cards()
            if uid not in all_cards:
                return False, f"Thẻ {uid} không tồn tại"
            
            # Kiểm tra thẻ có đang trong bãi không
            card_data = all_cards[uid]
            if card_data.get('status') == 1:
                return False, f"Không thể xóa thẻ {uid} đang trong bãi xe"
            
            # Xóa thẻ
            del all_cards[uid]
            
            # Lưu file
            success, error_msg = self.file_manager.atomic_write_json(
                self.CARDS_FILE, 
                all_cards
            )
            
            if success:
                self.log_service.add_log(uid, LogAction.CARD_DELETED)
                logger.info(f"🗑️ Đã xóa thẻ {uid}")
                return True, f"Xóa thẻ {uid} thành công"
            else:
                return False, f"Lỗi lưu dữ liệu: {error_msg}"
                
        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"
    
    # ==================== Statistics & Analytics ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Tính toán thống kê cơ bản (từ actual implementation)"""
        try:
            cards = self.get_all_cards()
            total_cards = len(cards)
            inside_count = sum(1 for card in cards.values() if card.status == 1)
            outside_count = total_cards - inside_count
            
            return {
                "total_cards": total_cards,
                "inside_parking": inside_count,
                "outside_parking": outside_count,
                "occupancy_rate": (inside_count / total_cards * 100) if total_cards > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
```

**Các patterns thiết kế được áp dụng**:

**1. Service Layer Pattern**:
- **Tách biệt logic**: API chỉ xử lý request/response, business logic trong services
- **Single Responsibility**: Mỗi method chỉ làm 1 việc cụ thể
- **Dependency Injection**: Các service được inject vào nhau (FileManager, LogService)

**2. Error Handling Strategy**:
- **Graceful Degradation**: App vẫn chạy được khi gặp lỗi
- **Comprehensive Logging**: Log chi tiết mọi thao tác quan trọng
- **User-Friendly Messages**: Thông báo lỗi dễ hiểu

**3. Data Validation Layers**:
- **Input Validation**: Kiểm tra format, length, data type
- **Business Rules**: Business logic của hệ thống
- **Error Response**: Log lỗi và trả về message phù hợp

**4. Transaction-like Operations**:
- **Atomic Writes**: Đảm bảo data consistency
- **Rollback Mechanism**: Có thể hoàn tác khi lỗi
- **State Management**: Quản lý trạng thái chính xác

**5. Tối ưu hóa hiệu suất**:
- **Chiến lược bộ nhớ đệm**: Lưu trữ tạm dữ liệu truy cập thường xuyên
- **Tải chậm**: Chỉ tải dữ liệu khi thực sự cần thiết
- **Thao tác hàng loạt**: Nhóm nhiều thao tác lại với nhau

**6. Ví dụ business logic thực tế**:
- **Validation dữ liệu**: Kiểm tra định dạng UID, chuẩn hóa thành chữ hoa
- **Backup tự động**: Tự động sao lưu sau các thay đổi quan trọng  
- **Logging hoạt động**: Ghi lại các hành động tạo, xóa thẻ cho audit

#### 4. **Data Models (models/card.py)**

📁 **File: `backend/models/card.py`**

```python
class ParkingCard:
    """
    Lớp ParkingCard - Đại diện cho một thẻ đỗ xe với khả năng tracking thời gian
    
    Attributes:
        uid: Mã định danh duy nhất của thẻ RFID
        status: Trạng thái (0=ngoài bãi, 1=trong bãi)  
        entry_time: Thời gian vào bãi (ISO format string)
        exit_time: Thời gian ra bãi (ISO format string)
        created_at: Thời gian tạo thẻ lần đầu
        parking_duration: Thời lượng đỗ xe được tính toán
    """
    
    def __init__(self, uid: str, status: int = 0, entry_time: Optional[str] = None, 
                 exit_time: Optional[str] = None, created_at: Optional[str] = None):
        """
        Khởi tạo đối tượng thẻ đỗ xe
        
        Args:
            uid: Mã định danh duy nhất của thẻ RFID
            status: Trạng thái thẻ (0=ngoài bãi, 1=trong bãi)
            entry_time: Timestamp ISO khi xe vào bãi (string)
            exit_time: Timestamp ISO khi xe ra bãi (string)
            created_at: Timestamp ISO khi tạo thẻ lần đầu (string)
        """
        self.uid = uid.upper().strip()  # Chuẩn hóa UID
        self.status = status
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.parking_duration = None
        
        # Tính toán thời lượng đỗ xe nếu có đủ thông tin
        self._calculate_parking_duration()
    
    def update_status(self, new_status: int) -> Dict[str, Any]:
        """Update card status với proper time tracking và validation"""
        old_status = self.status
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Kiểm tra trạng thái có thay đổi không
        if new_status == old_status:
            return {
                "success": False,
                "message": f"Thẻ {self.uid} đã ở trạng thái {new_status}",
                "action": "no_change"
            }
        
        self.status = new_status
        
        if new_status == 1:  # Vào bãi
            self.entry_time = current_time
            self.exit_time = None  # Clear exit time cũ
            action = "entry"
            message = f"Xe vào bãi - Thẻ {self.uid}"
        else:  # Ra khỏi bãi (new_status == 0)
            self.exit_time = current_time
            self._calculate_parking_duration()
            action = "exit"
            duration_text = self.parking_duration["display"] if self.parking_duration else "N/A"
            message = f"Xe ra khỏi bãi - Thẻ {self.uid} - Thời gian đỗ: {duration_text}"
        
        return {
            "success": True,
            "message": message,
            "action": action,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": current_time,
            "parking_duration": self.parking_duration
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for JSON serialization"""
        result = {
            "uid": self.uid,
            "status": self.status,
            "created_at": self.created_at
        }
        
        if self.entry_time:
            result["entry_time"] = self.entry_time
        if self.exit_time:
            result["exit_time"] = self.exit_time
        if self.parking_duration:
            result["parking_duration"] = self.parking_duration
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingCard':
        """Create ParkingCard instance from dictionary"""
        return cls(
            uid=data["uid"],
            status=data.get("status", 0),
            entry_time=data.get("entry_time"),
            exit_time=data.get("exit_time"),
            created_at=data.get("created_at")
        )
```

**Chức năng**:
- Đại diện cho data model của thẻ đỗ xe
- Encapsulate business logic của thẻ (validate, calculate duration)
- Cung cấp methods để serialize/deserialize dữ liệu

### 💾 **Lưu trữ dữ liệu (Tệp JSON)**

Thay vì dùng database phức tạp, project sử dụng **JSON files** để lưu trữ:

```json
{
  "A1B2C3D4": {
    "uid": "A1B2C3D4",
    "status": 1,
    "entry_time": "2024-01-15T10:30:00",
    "exit_time": null,
    "created_at": "2024-01-15T09:00:00"
  },
  "E5F6G7H8": {
    "uid": "E5F6G7H8", 
    "status": 0,
    "entry_time": "2024-01-15T08:00:00",
    "exit_time": "2024-01-15T10:00:00",
    "created_at": "2024-01-14T15:30:00"
  }
}
```

**Ưu điểm**:
- Đơn giản, không cần cài database
- Dễ backup và restore
- Human-readable format
- Phù hợp cho prototype và small-scale

---

## 🔌 Lớp phần cứng - Vi điều khiển

### 🎯 **Arduino UNO R4 WiFi**

📁 **File: `hardware/uno_r4_wifi/uno_r4_wifi.ino`**

```cpp
/*
 * BÃI ĐỖ XE THÔNG MINH - ARDUINO UNO R4 WiFi
 * Dual RFID + Servo Barriers + WiFi AP
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <WiFiS3.h>   // Arduino UNO R4 WiFi library
#include <string.h>

// RFID RC522 - DUAL READERS
// IN Reader
#define SS_PIN_IN 10
#define RST_PIN_IN 9
MFRC522 rfidIn(SS_PIN_IN, RST_PIN_IN);

// OUT Reader
#define SS_PIN_OUT 7
#define RST_PIN_OUT 8
MFRC522 rfidOut(SS_PIN_OUT, RST_PIN_OUT);

// SERVO MOTORS
Servo servoIn, servoOut;
#define SERVO_IN_PIN 5
#define SERVO_OUT_PIN 6
#define SERVO_CLOSED_ANGLE 0    // Đóng barrier
#define SERVO_OPEN_ANGLE 90     // Mở barrier

// ULTRASONIC SENSORS
#define TRIG_IN 3
#define ECHO_IN 4
#define TRIG_OUT 2
#define ECHO_OUT A0

// WIFI CONFIG
const char* apSsid = "UNO-R4-AP";
const char* apPassword = "12345678";
String serverIP = "192.168.4.3";      // IP của Python server
uint16_t serverPort = 5000;

// NON-BLOCKING STATE MACHINE
enum BarrierState {
  IDLE, OPENING, WAITING_VEHICLE, VEHICLE_PRESENT, CLOSING, TIMEOUT_CLOSING
};

struct BarrierControl {
  BarrierState state;
  unsigned long stateStartTime;
  int presentCount, absentCount;
  bool vehicleDetected;
  Servo* servo;
  int trigPin, echoPin;
  String name;
};

BarrierControl barrierIn, barrierOut;

void setup() {
  Serial.begin(9600);
  Serial.println("🚀 BÃI ĐỖ XE THÔNG MINH");
  
  // Khởi tạo RFID, Servo, Ultrasonic
  SPI.begin();
  rfidIn.PCD_Init();
  rfidOut.PCD_Init();
  servoIn.attach(SERVO_IN_PIN);
  servoOut.attach(SERVO_OUT_PIN);
  
  // Khởi tạo Barriers với state machine
  initBarrier(barrierIn, &servoIn, TRIG_IN, ECHO_IN, "IN");
  initBarrier(barrierOut, &servoOut, TRIG_OUT, ECHO_OUT, "OUT");
  
  // WiFi AP với IP tĩnh 192.168.4.2
  IPAddress staticIP(192, 168, 4, 2);
  WiFi.config(staticIP, staticIP, IPAddress(255, 255, 255, 0));
  WiFi.beginAP(apSsid, apPassword, 1);
  Serial.println("✅ WiFi AP: " + String(apSsid));
  Serial.println("📡 IP tĩnh: " + WiFi.localIP().toString());
}

void loop() {
  // Cập nhật state machine cho cả 2 barriers
  updateBarrier(barrierIn);
  updateBarrier(barrierOut);

  // Dual RFID scanning với cooldown riêng biệt
  static unsigned long lastRfidTimeIN = 0, lastRfidTimeOUT = 0;
  static String lastUID_IN = "", lastUID_OUT = "";
  
  // RFID IN reader
  if (millis() - lastRfidTimeIN > 100) {
    String uidIn = readRFID(rfidIn, "IN");
    if (uidIn != "" && uidIn != lastUID_IN) {
      lastUID_IN = uidIn;
      lastRfidTimeIN = millis();
      sendRFIDToServer(uidIn, "IN");
    }
    if (millis() - lastRfidTimeIN > 3000) lastUID_IN = "";
  }
  
  // RFID OUT reader  
  if (millis() - lastRfidTimeOUT > 100) {
    String uidOut = readRFID(rfidOut, "OUT");
    if (uidOut != "" && uidOut != lastUID_OUT) {
      lastUID_OUT = uidOut;
      lastRfidTimeOUT = millis();
      sendRFIDToServer(uidOut, "OUT");
    }
    if (millis() - lastRfidTimeOUT > 3000) lastUID_OUT = "";
  }
  
  delay(10);
}

// State machine cập nhật barrier non-blocking
void updateBarrier(BarrierControl& barrier) {
  unsigned long elapsed = millis() - barrier.stateStartTime;
  long distance = readDistanceCM(barrier.trigPin, barrier.echoPin);
  bool isPresent = (distance > 0 && distance <= 10); // 10cm threshold

  switch (barrier.state) {
    case IDLE: break; // Chờ lệnh mở
    
    case OPENING:
      if (elapsed > 2000) {
        barrier.state = WAITING_VEHICLE;
        barrier.stateStartTime = millis();
        Serial.println("🚪 Barrier " + barrier.name + " đã mở - chờ xe");
      }
      break;
      
    case WAITING_VEHICLE:
      if (isPresent) {
        barrier.presentCount++;
        if (barrier.presentCount >= 3) {
          barrier.state = VEHICLE_PRESENT;
          barrier.stateStartTime = millis();
          Serial.println("🟢 Xe tại barrier " + barrier.name);
        }
      } else barrier.presentCount = 0;
      
      if (elapsed > 30000) { // Timeout 30s
        barrier.state = TIMEOUT_CLOSING;
        barrier.servo->write(SERVO_CLOSED_ANGLE);
      }
      break;
      
    case VEHICLE_PRESENT:
      if (!isPresent) {
        barrier.absentCount++;
        if (barrier.absentCount >= 3) {
          barrier.state = CLOSING;
          barrier.servo->write(SERVO_CLOSED_ANGLE);
          Serial.println("🔵 Xe đã qua barrier " + barrier.name);
        }
      } else barrier.absentCount = 0;
      break;
      
    case CLOSING:
    case TIMEOUT_CLOSING:
      if (elapsed > 2000) {
        barrier.state = IDLE;
        Serial.println("✅ Barrier " + barrier.name + " đã đóng");
      }
      break;
  }
}

// Mở barrier nếu đang IDLE
void openBarrier(BarrierControl& barrier) {
  if (barrier.state == IDLE) {
    barrier.servo->write(SERVO_OPEN_ANGLE);
    barrier.state = OPENING;
    barrier.stateStartTime = millis();
    Serial.println("🚪📂 Mở barrier " + barrier.name);
  } else {
    Serial.println("⚠️ Barrier " + barrier.name + " đang bận");
  }
}

// Gửi RFID đến server
void sendRFIDToServer(const String& uid, const String& direction) {
  WiFiClient client;
  if (client.connect(serverIP.c_str(), serverPort)) {
    String jsonBody = "{\"card_id\":\"" + uid + "\",\"direction\":\"" + direction + "\"}";
    String httpRequest = "POST /api/cards/scan HTTP/1.1\r\n";
    httpRequest += "Host: " + serverIP + "\r\n";
    httpRequest += "Content-Type: application/json\r\n";
    httpRequest += "Content-Length: " + String(jsonBody.length()) + "\r\n\r\n";
    httpRequest += jsonBody;
    
    client.print(httpRequest);
    
    String response = "";
    unsigned long timeout = millis() + 1000;
    while (client.connected() && millis() < timeout) {
      if (client.available()) {
        response += client.readString();
        break;
      }
      delay(10);
    }
    client.stop();
    
    // Parse response và điều khiển barrier
    if (response.indexOf("\"success\":true") >= 0) {
      if (direction == "IN") openBarrier(barrierIn);
      else if (direction == "OUT") openBarrier(barrierOut);
    } else {
      Serial.println("❌ Thẻ không hợp lệ: " + uid);
    }
  }
}

// ... (các hàm helper: initBarrier, readRFID, readDistanceCM)
```

**Chức năng**:
- Đọc thẻ RFID khi có người quét
- Kết nối WiFi và gửi UID lên server
- Nhận response và thực hiện hành động phù hợp

### 📡 **ESP32 Sensors**

📁 **File: `hardware/esp32_sensors/esp32_main.ino`**

```cpp
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <WebServer.h>

// ================== CẤU HÌNH WIFI ==================
const char* ssid = "UNO-R4-AP";           // Kết nối vào WiFi của UNO R4
const char* password = "12345678";

// Cấu hình IP tĩnh cho ESP32
IPAddress local_IP(192, 168, 4, 5);      // IP tĩnh của ESP32
IPAddress gateway(192, 168, 4, 2);       // Gateway (UNO R4 WiFi)
IPAddress subnet(255, 255, 255, 0);      // Subnet mask

// HTTP Server cho Pull Model
WebServer server(80);

// Dữ liệu hiện tại cho Pull Model
int currentDistances[6] = {-1, -1, -1, -1, -1, -1};

// WiFi reconnection management
unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 30000; // Check every 30 seconds
const unsigned long WIFI_RECONNECT_TIMEOUT = 10000; // 10s timeout for reconnect

// ================== CHÂN KẾT NỐI ==================
#define chanDuLieu   23   // DS của 74HC595
#define chanClock    18   // SH_CP của 74HC595
#define chanLatch    5    // ST_CP của 74HC595

// 74HC595 điều khiển MOSFET để ON/OFF nguồn VCC của từng sensor
// Q1-Q6 → MOSFET Gate → VCC switching cho từng HY-SRF05
// Chỉ 1 sensor có nguồn VCC tại 1 thời điểm!

// HY-SRF05 nối trực tiếp với ESP32 (TRIG/ECHO chung)
#define chanSensor1  13   // HY-SRF05 #1 (TRIG/ECHO) - VCC từ Q1→MOSFET
#define chanSensor2  14   // HY-SRF05 #2 (TRIG/ECHO) - VCC từ Q2→MOSFET
#define chanSensor3  27   // HY-SRF05 #3 (TRIG/ECHO) - VCC từ Q3→MOSFET
#define chanSensor4  26   // HY-SRF05 #4 (TRIG/ECHO) - VCC từ Q4→MOSFET
#define chanSensor5  25   // HY-SRF05 #5 (TRIG/ECHO) - VCC từ Q5→MOSFET
#define chanSensor6  33   // HY-SRF05 #6 (TRIG/ECHO) - VCC từ Q6→MOSFET

// Mảng chứa các pin sensor (TRIG/ECHO)
int sensorPins[] = {chanSensor1, chanSensor2, chanSensor3, chanSensor4, chanSensor5, chanSensor6};

// Bit patterns để bật nguồn VCC cho từng sensor qua MOSFET
byte qPatterns[] = {
  0b00000010,  // Q1 HIGH → MOSFET ON → VCC cho sensor #1
  0b00000100,  // Q2 HIGH → MOSFET ON → VCC cho sensor #2  
  0b00001000,  // Q3 HIGH → MOSFET ON → VCC cho sensor #3
  0b00010000,  // Q4 HIGH → MOSFET ON → VCC cho sensor #4
  0b00100000,  // Q5 HIGH → MOSFET ON → VCC cho sensor #5
  0b01000000   // Q6 HIGH → MOSFET ON → VCC cho sensor #6
};

byte trangThai = 0;

// ================== HTTP SERVER ENDPOINTS (PULL MODEL) ==================
void handleGetData() {
  // Trả về dữ liệu theo format server expect
  DynamicJsonDocument doc(1024);
  
  doc["success"] = true;
  doc["soIC"] = 1;  // Số IC 74HC595
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array ở root level (format cũ)
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);  // Lỗi = trống
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info as bonus
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", response);
  
  Serial.println("Server requested data: " + response);
}

void handleDetect() {
  // Lệnh detect lại cảm biến (giống như reset)
  Serial.println("Server requested detect/reset");
  
  // Đọc lại tất cả cảm biến
  docTatCaCamBien();
  
  DynamicJsonDocument doc(1024);
  doc["success"] = true;
  doc["message"] = "Đã detect lại 6 cảm biến";
  doc["soIC"] = 1;
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array sau khi reset
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
  }
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// ================== POWER CONTROL VIA 74HC595 ==================
void capNhat595() {
  digitalWrite(chanLatch, LOW);
  shiftOut(chanDuLieu, chanClock, MSBFIRST, trangThai);
  digitalWrite(chanLatch, HIGH);
}

void tatTatCaNguon() {
  trangThai = 0b00000000;  // Tất cả MOSFET OFF
  capNhat595();
}

void batNguonSensor(int sensorNumber) {
  if (sensorNumber >= 1 && sensorNumber <= 6) {
    trangThai = qPatterns[sensorNumber - 1];  // Chỉ 1 MOSFET ON
    capNhat595();
  }
}

// ================== ĐỌC SENSOR VỚI POWER SWITCHING ==================
long docKhoangCachCM(int sensorNumber) {
  if (sensorNumber < 1 || sensorNumber > 6) return -1;
  
  int sensorPin = sensorPins[sensorNumber - 1];
  
  // Đợi sensor khởi động (HY-SRF05 cần ~200ms sau khi có VCC)
  delay(200);
  
  // Cấu hình chân là OUTPUT để gửi TRIG pulse  
  pinMode(sensorPin, OUTPUT);
  digitalWrite(sensorPin, LOW);
  delayMicroseconds(2);
  digitalWrite(sensorPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensorPin, LOW);
  
  // Chuyển chân thành INPUT để đọc ECHO
  pinMode(sensorPin, INPUT);
  
  // Đọc thời gian ECHO (timeout 40ms)
  long thoiGian = pulseIn(sensorPin, HIGH, 40000);
  
  if (thoiGian == 0) return -1;  // timeout
  return thoiGian / 29.1 / 2;
}

void docTatCaCamBien() {
  Serial.println("Starting sensor scan with POWER SWITCHING...");
  
  for (int s = 1; s <= 6; s++) {
    Serial.print("Reading Sensor #" + String(s) + ": ");
    
    // TẮT TẤT CẢ nguồn trước
    tatTatCaNguon();
    delay(100);
    
    // BẬT NGUỒN cho sensor hiện tại qua MOSFET
    batNguonSensor(s);
    Serial.print("VCC ON → ");
    
    // Đọc sensor
    long kc = docKhoangCachCM(s);
    currentDistances[s-1] = kc;
    
    if (kc == -1) {
      Serial.println("TIMEOUT");
    } else {
      Serial.println(String(kc) + "cm");
    }
    
    // TẮT nguồn sensor này (tiết kiệm điện)
    tatTatCaNguon();
    delay(50);
  }
  
  tatTatCaNguon();
  Serial.println("Power switching scan completed!");
}

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Parking Sensors");
  
  // Cấu hình chân 74HC595
  pinMode(chanDuLieu, OUTPUT);
  pinMode(chanClock, OUTPUT);
  pinMode(chanLatch, OUTPUT);
  
  // Cấu hình chân sensor pins
  for (int i = 0; i < 6; i++) {
    pinMode(sensorPins[i], OUTPUT);
    digitalWrite(sensorPins[i], LOW);
  }
  
  // Tắt tất cả nguồn sensor ban đầu
  tatTatCaNguon();
  delay(500);
  
  // Cấu hình IP tĩnh
  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.println("ESP32 IP: " + WiFi.localIP().toString());
  
  // Khởi động HTTP Server cho Pull Model
  server.on("/data", HTTP_GET, handleGetData);
  server.on("/detect", HTTP_POST, handleDetect);
  server.begin();
  
  Serial.println("HTTP Server started on port 80");
  Serial.println("Pull model only - Backend polls every 30 minutes");
}

void loop() {
  // Xử lý HTTP requests (Pull Model only)
  server.handleClient();
  delay(100);
}

// ... (các hàm helper: initBarrier, readRFID, readDistanceCM)
```

**Chức năng chính**:
- **State Machine**: Non-blocking barriers control với multiple states
- **Dual RFID**: Đọc đồng thời 2 readers IN/OUT với cooldown riêng biệt  
- **HTTP Communication**: Gửi JSON request đến Python server
- **Safety Logic**: Timeout protection và collision detection

### 📡 **ESP32 Sensors**

📁 **File: `hardware/esp32_sensors/esp32_main.ino`**

```cpp
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <WebServer.h>

// ================== CẤU HÌNH WIFI ==================
const char* ssid = "UNO-R4-AP";           // Kết nối vào WiFi của UNO R4
const char* password = "12345678";

// Cấu hình IP tĩnh cho ESP32
IPAddress local_IP(192, 168, 4, 5);      // IP tĩnh của ESP32
IPAddress gateway(192, 168, 4, 2);       // Gateway (UNO R4 WiFi)
IPAddress subnet(255, 255, 255, 0);      // Subnet mask

// HTTP Server cho Pull Model
WebServer server(80);

// Dữ liệu hiện tại cho Pull Model
int currentDistances[6] = {-1, -1, -1, -1, -1, -1};

// ================== CHÂN KẾT NỐI ==================
#define chanDuLieu   23   // DS của 74HC595
#define chanClock    18   // SH_CP của 74HC595
#define chanLatch    5    // ST_CP của 74HC595

// 74HC595 điều khiển MOSFET để ON/OFF nguồn VCC của từng sensor
// Q1-Q6 → MOSFET Gate → VCC switching cho từng HY-SRF05
// Chỉ 1 sensor có nguồn VCC tại 1 thời điểm!

// HY-SRF05 nối trực tiếp với ESP32 (TRIG/ECHO chung)
#define chanSensor1  13   // HY-SRF05 #1 (TRIG/ECHO) - VCC từ Q1→MOSFET
#define chanSensor2  14   // HY-SRF05 #2 (TRIG/ECHO) - VCC từ Q2→MOSFET
#define chanSensor3  27   // HY-SRF05 #3 (TRIG/ECHO) - VCC từ Q3→MOSFET
#define chanSensor4  26   // HY-SRF05 #4 (TRIG/ECHO) - VCC từ Q4→MOSFET
#define chanSensor5  25   // HY-SRF05 #5 (TRIG/ECHO) - VCC từ Q5→MOSFET
#define chanSensor6  33   // HY-SRF05 #6 (TRIG/ECHO) - VCC từ Q6→MOSFET

// Mảng chứa các pin sensor (TRIG/ECHO)
int sensorPins[] = {chanSensor1, chanSensor2, chanSensor3, chanSensor4, chanSensor5, chanSensor6};

// Bit patterns để bật nguồn VCC cho từng sensor qua MOSFET
byte qPatterns[] = {
  0b00000010,  // Q1 HIGH → MOSFET ON → VCC cho sensor #1
  0b00000100,  // Q2 HIGH → MOSFET ON → VCC cho sensor #2  
  0b00001000,  // Q3 HIGH → MOSFET ON → VCC cho sensor #3
  0b00010000,  // Q4 HIGH → MOSFET ON → VCC cho sensor #4
  0b00100000,  // Q5 HIGH → MOSFET ON → VCC cho sensor #5
  0b01000000   // Q6 HIGH → MOSFET ON → VCC cho sensor #6
};

byte trangThai = 0;

// ================== HTTP SERVER ENDPOINTS (PULL MODEL) ==================
void handleGetData() {
  // Trả về dữ liệu theo format server expect
  DynamicJsonDocument doc(1024);
  
  doc["success"] = true;
  doc["soIC"] = 1;  // Số IC 74HC595
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array ở root level (format cũ)
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);  // Lỗi = trống
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info as bonus
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", response);
  
  Serial.println("Server requested data: " + response);
}

void handleDetect() {
  // Lệnh detect lại cảm biến (giống như reset)
  Serial.println("Server requested detect/reset");
  
  // Đọc lại tất cả cảm biến
  docTatCaCamBien();
  
  DynamicJsonDocument doc(1024);
  doc["success"] = true;
  doc["message"] = "Đã detect lại 6 cảm biến";
  doc["soIC"] = 1;
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array sau khi reset
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
  }
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// ================== POWER CONTROL VIA 74HC595 ==================
void capNhat595() {
  digitalWrite(chanLatch, LOW);
  shiftOut(chanDuLieu, chanClock, MSBFIRST, trangThai);
  digitalWrite(chanLatch, HIGH);
}

void tatTatCaNguon() {
  trangThai = 0b00000000;  // Tất cả MOSFET OFF
  capNhat595();
}

void batNguonSensor(int sensorNumber) {
  if (sensorNumber >= 1 && sensorNumber <= 6) {
    trangThai = qPatterns[sensorNumber - 1];  // Chỉ 1 MOSFET ON
    capNhat595();
  }
}

// ================== ĐỌC SENSOR VỚI POWER SWITCHING ==================
long docKhoangCachCM(int sensorNumber) {
  if (sensorNumber < 1 || sensorNumber > 6) return -1;
  
  int sensorPin = sensorPins[sensorNumber - 1];
  
  // Đợi sensor khởi động (HY-SRF05 cần ~200ms sau khi có VCC)
  delay(200);
  
  // Cấu hình chân là OUTPUT để gửi TRIG pulse  
  pinMode(sensorPin, OUTPUT);
  digitalWrite(sensorPin, LOW);
  delayMicroseconds(2);
  digitalWrite(sensorPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensorPin, LOW);
  
  // Chuyển chân thành INPUT để đọc ECHO
  pinMode(sensorPin, INPUT);
  
  // Đọc thời gian ECHO (timeout 40ms)
  long thoiGian = pulseIn(sensorPin, HIGH, 40000);
  
  if (thoiGian == 0) return -1;  // timeout
  return thoiGian / 29.1 / 2;
}

void docTatCaCamBien() {
  Serial.println("Starting sensor scan with POWER SWITCHING...");
  
  for (int s = 1; s <= 6; s++) {
    Serial.print("Reading Sensor #" + String(s) + ": ");
    
    // TẮT TẤT CẢ nguồn trước
    tatTatCaNguon();
    delay(100);
    
    // BẬT NGUỒN cho sensor hiện tại qua MOSFET
    batNguonSensor(s);
    Serial.print("VCC ON → ");
    
    // Đọc sensor
    long kc = docKhoangCachCM(s);
    currentDistances[s-1] = kc;
    
    if (kc == -1) {
      Serial.println("TIMEOUT");
    } else {
      Serial.println(String(kc) + "cm");
    }
    
    // TẮT nguồn sensor này (tiết kiệm điện)
    tatTatCaNguon();
    delay(50);
  }
  
  tatTatCaNguon();
  Serial.println("Power switching scan completed!");
}

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Parking Sensors");
  
  // Cấu hình chân 74HC595
  pinMode(chanDuLieu, OUTPUT);
  pinMode(chanClock, OUTPUT);
  pinMode(chanLatch, OUTPUT);
  
  // Cấu hình chân sensor pins
  for (int i = 0; i < 6; i++) {
    pinMode(sensorPins[i], OUTPUT);
    digitalWrite(sensorPins[i], LOW);
  }
  
  // Tắt tất cả nguồn sensor ban đầu
  tatTatCaNguon();
  delay(500);
  
  // Cấu hình IP tĩnh
  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.println("ESP32 IP: " + WiFi.localIP().toString());
  
  // Khởi động HTTP Server cho Pull Model
  server.on("/data", HTTP_GET, handleGetData);
  server.on("/detect", HTTP_POST, handleDetect);
  server.begin();
  
  Serial.println("HTTP Server started on port 80");
  Serial.println("Pull model only - Backend polls every 30 minutes");
}

void loop() {
  // Xử lý HTTP requests (Pull Model only)
  server.handleClient();
  delay(100);
}
```

**Chức năng chính**:
- **Power Switching**: Chỉ 1 sensor có nguồn VCC tại 1 thời điểm qua 74HC595 + MOSFET
- **Pull Model**: Backend polling endpoints `/data` và `/detect` mỗi 30 phút  
- **Sensor Management**: Sequential reading với power management để tránh nhiễu
- **JSON Response**: Format chuẩn `{"data": [0,1,0,1,0,0]}` cho 6 parking slots

---

## 🔗 Tương Tác Giữa Các Components

### 🔄 **Luồng Dữ Liệu**

**1. Hardware → Backend:**
- Arduino UNO R4 WiFi: Gửi HTTP POST `/api/cards/scan` khi đọc được RFID
- ESP32: Backend pull data từ endpoint `/data` mỗi 30 phút

**2. Backend → Frontend:**
- REST API endpoints: `/api/cards/*`, `/api/cards/statistics`, `/api/cards/logs`
- Frontend polling: Auto-refresh dashboard mỗi 30 giây

**3. Data Flow Sequence:**
```
RFID Scan → Arduino → HTTP POST → Backend → JSON Update → Frontend Poll → UI Update
Sensor → ESP32 → HTTP GET → Backend → Parking Status → Dashboard Display
```

### 📡 **Network Architecture**

```
192.168.4.2 (Arduino UNO R4 WiFi - Access Point)
     │
     ├── 192.168.4.3 (Python Flask Server)
     ├── 192.168.4.5 (ESP32 Sensors)  
     └── 192.168.4.x (Client devices - Frontend)
```

### 🛠️ **Component Responsibilities**

#### **Arduino UNO R4 WiFi**:
- **RFID Processing**: Dual readers cho IN/OUT traffic
- **Barrier Control**: Servo motors với safety logic  
- **Network Hub**: WiFi Access Point cho toàn bộ hệ thống
- **Hardware Integration**: Ultrasonic sensors cho vehicle detection

#### **ESP32**:
- **Parking Detection**: 6 ultrasonic sensors với power switching
- **Data Provider**: HTTP server cho pull model
- **Power Management**: 74HC595 + MOSFET switching circuit
- **Sensor Optimization**: Sequential reading để tránh interference

#### **Python Backend**:
- **Business Logic**: Card validation, status management, logging
- **Data Persistence**: JSON file operations với atomic writes
- **API Gateway**: RESTful endpoints cho frontend và hardware
- **Background Services**: Automated backup, scheduled tasks

#### **React Frontend**:
- **User Interface**: Dashboard, card management, real-time monitoring
- **State Management**: React hooks cho data synchronization  
- **API Integration**: Axios client với error handling
- **Responsive Design**: Multi-device compatibility

---

## 🔧 Cấu Hình Hệ Thống

### ⚙️ **Backend Configuration**

📁 **File: `backend/config/config.py`**

```python
"""
Configuration Management - Quản lý cấu hình cho backend hệ thống bãi đỗ xe

Chứa tất cả cấu hình:
- File paths và directories
- Network configuration (API server, ESP32, UNO R4)
- Auto IP detection cho UNO R4 WiFi network
- Mock server settings cho testing
- Flask app configurations
"""
import os
from pathlib import Path

# Thư mục gốc của project
BASE_DIR = Path(__file__).parent.parent

# Files lưu dữ liệu
DATA_DIR = BASE_DIR / "data"
CARDS_FILE = DATA_DIR / "cards.json"          # File lưu thông tin các thẻ đã đăng ký
UNKNOWN_CARDS_FILE = DATA_DIR / "unknown_cards.json"  # File lưu các thẻ lạ

# Cấu hình mạng
def detect_api_host():
    """Tự động phát hiện IP interface kết nối với UNO R4 WiFi"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.4.2", 80))
        host = s.getsockname()[0]
        s.close()
        print(f"🎯 Server sẽ chạy trên: {host}")
        return host
    except:
        print("⚠️ Không phát hiện UNO R4, sử dụng 0.0.0.0")
        return "0.0.0.0"

API_HOST = detect_api_host()
API_PORT = 5000
DEBUG_MODE = True

# ESP32 configuration
ESP32_IP = "192.168.4.5"
ESP32_PORT = 80
ESP32_TIMEOUT = 10
DETECTION_THRESHOLD = 10  # cm - threshold for parking detection

# Cấu hình backup và logging
BACKUP_INTERVAL = 3600  # 1 giờ
MAX_BACKUPS = 24       # Giữ lại 24 backup (1 ngày)

# UNO R4 WiFi configuration  
UNO_R4_IP = "192.168.4.2"  # IP tĩnh của UNO R4
UNO_R4_AP_SSID = "UNO-R4-AP"

# Frontend configuration
FRONTEND_BUILD_DIR = BASE_DIR.parent / "frontend" / "build"

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = DEBUG_MODE
    HOST = API_HOST
    PORT = API_PORT

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 🌐 **Network Configuration**

#### **IP Address Plan**:
- **192.168.4.2**: Arduino UNO R4 WiFi (Gateway + Access Point)
- **192.168.4.3**: Python Flask Server  
- **192.168.4.5**: ESP32 Sensors
- **192.168.4.x**: Client devices (laptops, phones)

#### **Port Allocation**:
- **Port 80**: ESP32 HTTP server, Arduino web interface
- **Port 5000**: Python Flask API server
- **Port 3000**: React development server

### 🔐 **Security Configuration**

📁 **File: `backend/config/cors.py`**

```python
"""
CORS configuration for frontend-backend communication
"""
from flask_cors import CORS

def init_cors(app):
    """Initialize CORS for the Flask app"""
    CORS(app, 
         origins=[
             "http://localhost:3000",      # React development
             "http://127.0.0.1:3000",     # React development  
             "http://localhost:5000",      # Production build
             "http://127.0.0.1:5000",     # Production build
             "http://192.168.4.3:5000",   # Network access
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True
    )
    return app
```

---

## 📊 Data Models & JSON Schema

### 💾 **Parking Card Model**

📁 **File: `backend/models/card.py`**

```python
"""
Card Data Model - Model dữ liệu cho thẻ đỗ xe RFID

Chức năng chính:
- Lưu trữ thông tin thẻ RFID và trạng thái xe
- Tính toán thời gian đỗ xe tự động 
- Validation dữ liệu đầu vào
- Chuyển đổi giữa dict và object
- Real-time tracking cho xe đang trong bãi
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class ParkingCard:
    """
    Lớp ParkingCard - Đại diện cho một thẻ đỗ xe với khả năng tracking thời gian
    
    Attributes:
        uid: Mã định danh duy nhất của thẻ RFID
        status: Trạng thái (0=ngoài bãi, 1=trong bãi)  
        entry_time: Thời gian vào bãi (ISO format)
        exit_time: Thời gian ra bãi (ISO format)
        created_at: Thời gian tạo thẻ lần đầu
        parking_duration: Thời lượng đỗ xe được tính toán
    """
    
    def __init__(self, uid: str, status: int = 0, entry_time: Optional[str] = None, 
                 exit_time: Optional[str] = None, created_at: Optional[str] = None):
        """
        Khởi tạo đối tượng thẻ đỗ xe
        
        Args:
            uid: Mã định danh duy nhất của thẻ RFID
            status: Trạng thái thẻ (0=ngoài bãi, 1=trong bãi)
            entry_time: Timestamp ISO khi xe vào bãi (string)
            exit_time: Timestamp ISO khi xe ra bãi (string)
            created_at: Timestamp ISO khi tạo thẻ lần đầu (string)
        """
        self.uid = uid.upper().strip()  # Chuẩn hóa UID
        self.status = status
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.parking_duration = None
        
        # Tính toán thời lượng đỗ xe nếu có đủ thông tin
        self._calculate_parking_duration()
    
    def update_status(self, new_status: int) -> Dict[str, Any]:
        """Update card status với proper time tracking và validation"""
        old_status = self.status
        current_time = datetime.now(timezone.utc).isoformat()
        
        if new_status == old_status:
            return {
                "success": False,
                "message": f"Thẻ {self.uid} đã ở trạng thái {new_status}",
                "action": "no_change"
            }
        
        self.status = new_status
        
        if new_status == 1:  # Vào bãi
            self.entry_time = current_time
            self.exit_time = None
            action = "entry"
            message = f"Xe vào bãi - Thẻ {self.uid}"
        else:  # Ra khỏi bãi (new_status == 0)
            self.exit_time = current_time
            self._calculate_parking_duration()
            action = "exit"
            duration_text = self.parking_duration["display"] if self.parking_duration else "N/A"
            message = f"Xe ra khỏi bãi - Thẻ {self.uid} - Thời gian đỗ: {duration_text}"
        
        return {
            "success": True,
            "message": message,
            "action": action,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": current_time,
            "parking_duration": self.parking_duration
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for JSON serialization"""
        result = {
            "uid": self.uid,
            "status": self.status,
            "created_at": self.created_at
        }
        
        if self.entry_time:
            result["entry_time"] = self.entry_time
        if self.exit_time:
            result["exit_time"] = self.exit_time
        if self.parking_duration:
            result["parking_duration"] = self.parking_duration
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingCard':
        """Create ParkingCard instance from dictionary"""
        return cls(
            uid=data["uid"],
            status=data.get("status", 0),
            entry_time=data.get("entry_time"),
            exit_time=data.get("exit_time"),
            created_at=data.get("created_at")
        )
```

### 📋 **JSON Data Schemas**

#### **cards.json Structure**:
```json
{
  "12345678": {
    "uid": "12345678",
    "status": 1,
    "entry_time": "2025-10-18T08:30:00",
    "exit_time": null,
    "created_at": "2025-10-15T10:00:00"
  },
  "ABCDEF90": {
    "uid": "ABCDEF90", 
    "status": 0,
    "entry_time": null,
    "exit_time": "2025-10-18T17:45:00",
    "created_at": "2025-10-16T14:20:00"
  }
}

**4. Tính năng thời gian thực**:
- **Giám sát trực tiếp**: Đọc cảm biến liên tục
- **Thay đổi trạng thái**: Phát hiện sự kiện xe vào/ra
- **Sức khỏe hệ thống**: Sử dụng bộ nhớ, trạng thái WiFi, số lỗi

**5. Thiết kế API**:
- **GET /data**: Điểm cuối chính cho tất cả cảm biến
- **GET /slot?id=X**: Chi tiết cho 1 vị trí cụ thể
- **Hỗ trợ CORS**: Cho phép yêu cầu từ các nguồn khác từ frontend

**6. Tối ưu hóa hiệu suất**:
- **Mã không chặn**: Không sử dụng delay() trong vòng lặp chính
- **Quản lý bộ nhớ**: Tài liệu JSON tĩnh, dọn dẹp đúng cách
- **Lấy mẫu hiệu quả**: Thời gian tối ưu hóa cho độ chính xác

---

## 🔄 Luồng Hoạt Động Tổng Thể

### 🔍 **Chi Tiết Từng Bước - Luồng Hoạt Động Complete**

#### **Bước 1: Hardware Detection & Data Transmission**

```cpp
// 📁 File: hardware/uno_r4_wifi/uno_r4_wifi.ino
// Dual RFID readers (IN/OUT) với state machine non-blocking  
void loop() {
  // Cập nhật song song 2 barrier
  updateBarrier(barrierIn);
  updateBarrier(barrierOut);

  // Đọc RFID từ 2 readers
  String uidIn = readRFID(rfidIn, "IN");
  if (uidIn != "") {
    sendRFIDToServer(uidIn, "IN");
  }
  
  String uidOut = readRFID(rfidOut, "OUT");  
  if (uidOut != "") {
    sendRFIDToServer(uidOut, "OUT");
  }
  
  delay(10);
}
```


#### **Backend Processing (Actual Implementation)**
```python  
# 📁 File: backend/api/cards.py
@cards_bp.route('/scan', methods=['POST'])
def scan_card():
    """
    ESP32 card scan endpoint - Process card scan from hardware
    
    Expected JSON payload:
    {
        "card_id": "A1B2C3D4", 
        "timestamp": "2025-10-06T21:47:00Z"
    }
    
    Returns:
        JSON response with card status and action taken
    """
    try:
        logger.info("ESP32: Card scan received")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type must be application/json"
            }), 400
        
        # Validate and process card scan request
        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({
                "success": False,
                "error": "Missing card_id",
                "message": "card_id field is required"
            }), 400
        
        # Process card scan with direction-based logic
        # Full implementation handles IN/OUT readers, status validation, logging
        # Returns success/error response based on business rules
        
        # ... (Complete implementation in backend/api/cards.py line 750-900)
    
    except Exception as e:
        logger.error(f"Exception in scan_card: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
```

> **📁 Full Implementation**: File `backend/api/cards.py` contains complete scan_card function (150+ lines) with direction-based logic, validation, status updates, logging, and unknown card handling.

**Key Logic**:
- **IN reader**: Entry logic (status 0→1) 
- **OUT reader**: Exit logic (status 1→0)
- **Validation**: Card ID format and existence check
- **Unknown cards**: Automatic tracking and alerts
- **Logging**: Detailed audit trail with metadata

---

## 🔧 Cập Nhật Real-time & Hiệu Suất

### ⚡ **Hệ Thống Cập Nhật**

**Triển khai hiện tại**: Phương pháp HTTP polling đơn giản
- Dashboard tự động refresh mỗi 30 giây qua `setInterval()`
- Nút refresh thủ công có sẵn cho cập nhật ngay lập tức  
- Không sử dụng WebSocket - dùng HTTP API calls chuẩn
- Frontend polling các endpoints `/api/cards/statistics` và `/api/cards/logs`

**Lợi ích**: Đơn giản, đáng tin cậy, thân thiện với browser, có thể mở rộng mà không cần persistent connections

### 🚀 **Tính Năng Hiệu Suất**

- **Thao tác file nguyên tử**: Ngăn chặn corruption dữ liệu khi ghi JSON
- **Background tasks**: Hệ thống backup tự động qua threading
- **Validation đầu vào**: Validation toàn diện trên tất cả endpoints
- **Xử lý lỗi**: Xử lý lỗi nhiều lớp với logging chi tiết
- **Cấu hình CORS**: Chia sẻ tài nguyên cross-origin bảo mật

---

## �️ Security & Error Handling

### 🔒 **Security Measures**
- Input sanitization and validation for all API endpoints
- CORS configuration for secure frontend-backend communication
- Comprehensive error handling with proper HTTP status codes
- Audit logging for all card operations and system events

### ⚠️ **Error Handling**
- Frontend error boundaries and fallback mechanisms
- Backend exception handling with structured error responses
- Hardware retry logic for network operations
- Graceful degradation when components are offline

---

## � Development Tools & Future Enhancements

### 🛠️ **Development Setup**
- **Frontend**: React TypeScript with auto-reload development server
- **Backend**: Python Flask with virtual environment setup
- **Hardware**: Arduino IDE for microcontroller programming
- **API Testing**: cURL commands for endpoint validation

### 🔮 **Potential Improvements**
- Database migration (PostgreSQL/MySQL) for better performance
- JWT authentication for enhanced security
- Email/SMS notifications for system events
- Mobile app development with React Native
- Advanced analytics and reporting features

---

## 🎓 Project Summary

### 📝 **Technical Achievements**
1. **Full-stack Architecture**: React TypeScript frontend + Python Flask backend
2. **IoT Integration**: Arduino UNO R4 WiFi + ESP32 with RFID/ultrasonic sensors
3. **RESTful API Design**: Proper HTTP methods with comprehensive error handling
4. **Hardware Communication**: HTTP-based sensor data exchange
5. **Data Management**: JSON-based storage with backup/restore functionality
6. **Real-time Features**: Polling-based dashboard updates

### 💡 **Learning Outcomes**
- Layered architecture design and implementation
- API integration between frontend and backend
- IoT programming and sensor integration
- Error handling and logging best practices
- Multi-microcontroller project coordination
- Full development lifecycle management
