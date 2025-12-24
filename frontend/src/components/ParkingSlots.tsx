/**
 * ParkingSlots.tsx - Component quản lý và hiển thị trạng thái vị trí đỗ xe
 * Chức năng: Monitoring real-time từ ESP32, hiển thị sơ đồ bãi đỗ, auto refresh/reset
 */

import React, { useState, useEffect } from 'react';
import { parkingApi } from '../api';

/**
 * Interface định nghĩa cấu trúc dữ liệu từ ESP32 parking slots API
 */
interface ParkingSlotsData {
  success: boolean;              // Trạng thái thành công của API call
  esp32_data?: {                 // Dữ liệu từ ESP32 (optional nếu không connect được)
    soIC: number;                // Số lượng IC 74HC595 được sử dụng
    totalSensors: number;        // Tổng số cảm biến (thường = 6)
    timestamp: number;           // ESP32 uptime (milliseconds)
    data: number[];              // Array trạng thái slots (0=trống, 1=có xe)
  };
  summary?: {                    // Thống kê tổng hợp (được tính ở backend)
    total_slots: number;         // Tổng số vị trí
    occupied: number;            // Số vị trí đã có xe
    available: number;           // Số vị trí trống
    occupancy_rate: number;      // Tỷ lệ lấp đầy (%)
  };
  last_updated: string;          // Timestamp cập nhật cuối (ISO format)
  error?: string;                // Thông báo lỗi (nếu có)
}

/**
 * Props interface cho ParkingSlots component
 */
interface ParkingSlotsProps {
  /** Callback để quay lại trang chính */
  onBack: () => void;
}

/**
 * ParkingSlots Component - Main function
 * Quản lý monitoring real-time các vị trí đỗ xe từ ESP32
 */
const ParkingSlots: React.FC<ParkingSlotsProps> = ({ onBack }) => {
  
  // ================== STATE MANAGEMENT ==================
  
  /** Dữ liệu parking slots từ ESP32 */
  const [slotsData, setSlotsData] = useState<ParkingSlotsData | null>(null);
  
  /** Trạng thái loading khi thực hiện API calls */
  const [loading, setLoading] = useState(false);
  
  /** Thông báo cho user */
  const [message, setMessage] = useState('');
  
  /** Bật/tắt auto refresh */
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  /** Interval cho auto refresh (đơn vị: phút) */
  const [autoRefreshInterval, setAutoRefreshInterval] = useState(30);
  
  /** Bật/tắt auto reset cảm biến khi refresh */
  const [autoResetEnabled, setAutoResetEnabled] = useState(false); // FIXED: Tắt auto reset mặc định

  // ================== API FUNCTIONS ==================
  
  /**
   * Lấy dữ liệu parking slots từ ESP32
   * @param withReset - True nếu muốn reset cảm biến khi fetch
   */
  const fetchParkingSlots = async (withReset: boolean = false) => {
    try {
      // Chọn endpoint dựa trên có reset hay không
      const endpoint = withReset ? '/api/parking-slots?reset=true' : '/api/parking-slots';
      const response = await parkingApi.getParkingSlots(endpoint);
      
      // Backend response structure: { success, data: {...}, summary: {...}, reset_performed, message }
      // Convert to expected structure for component
      const data = {
        success: response.success,
        esp32_data: response.data?.esp32_data,
        summary: response.summary,
        last_updated: response.data?.last_updated || new Date().toISOString(),
        reset_performed: response.reset_performed,
        error: response.error,
        message: response.message
      };
      
      setSlotsData(data);
      
      // Hiển thị message nếu có reset
      if (withReset && data.reset_performed) {
        setMessage('✅ Đã làm mới dữ liệu cảm biến');
      } else {
        setMessage('');
      }
    } catch (error: any) {
      console.error('Failed to fetch parking slots:', error);
      // Xử lý các loại lỗi khác nhau
      if (error.response?.status === 503) {
        setMessage('❌ Không thể kết nối ESP32. Kiểm tra thiết bị có hoạt động không.');
      } else {
        setMessage('❌ Lỗi kết nối ESP32');
      }
    }
  };

  /**
   * Reset tất cả cảm biến ESP32
   * Function riêng biệt cho manual reset (không kèm fetch data)
   */
  const handleResetSensors = async () => {
    // Xác nhận với user trước khi reset
    if (!window.confirm('Reset tất cả cảm biến ESP32?\nQuá trình này có thể mất 30-60 giây.')) {
      return;
    }

    setLoading(true);
    setMessage('🔄 Đang reset cảm biến ESP32...');
    
    try {
      const message = await parkingApi.resetParkingSlots();
      setMessage(`✅ ${message}`);
      // Refresh data sau khi reset hoàn thành
      setTimeout(() => {
        fetchParkingSlots();
      }, 2000);
    } catch (error: any) {
      console.error('Failed to reset sensors:', error);
      setMessage('❌ Lỗi reset cảm biến ESP32');
    } finally {
      setLoading(false);
    }
  };

  // ================== EFFECTS ==================
  
  /**
   * Auto refresh effect với reset tùy chọn
   * Chạy định kỳ theo autoRefreshInterval
   * Có thể kèm auto reset nếu autoResetEnabled = true
   */
  useEffect(() => {
    if (autoRefresh) {
      fetchParkingSlots(false); // Lần đầu không reset
      const interval = setInterval(() => {
        fetchParkingSlots(autoResetEnabled); // Theo cài đặt auto reset
      }, autoRefreshInterval * 60 * 1000); // Convert phút sang ms
      return () => clearInterval(interval);
    }
  }, [autoRefresh, autoRefreshInterval, autoResetEnabled]);

  /**
   * Auto-clear message sau 5 giây
   * Cải thiện UX bằng cách tự động ẩn thông báo
   */
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  // ================== UTILITY FUNCTIONS ==================
  
  /**
   * Render sơ đồ bãi đỗ xe dạng grid
   * Tự động tính toán layout dựa trên số lượng slots
   * @returns JSX grid hiển thị trạng thái từng vị trí
   */
  const renderParkingGrid = () => {
    if (!slotsData?.esp32_data?.data) {
      return <div className="no-data">Không có dữ liệu cảm biến</div>;
    }

    const slots = slotsData.esp32_data.data;
    // Tính số cột tối ưu cho grid (square layout)
    const slotsPerRow = Math.ceil(Math.sqrt(slots.length));
    
    return (
      <div className="parking-grid" style={{ gridTemplateColumns: `repeat(${Math.min(slotsPerRow, 10)}, 1fr)` }}>
        {slots.map((status, index) => (
          <div 
            key={index}
            className={`parking-slot ${status === 1 ? 'occupied' : 'available'}`}
            title={`Vị trí ${index + 1}: ${status === 1 ? 'Có xe' : 'Trống'}`}
          >
            <div className="slot-number">{index + 1}</div>
            <div className="slot-status">
              {status === 1 ? '🚗' : '⬜'}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="parking-slots-page">
      <header className="page-header">
        <button className="back-btn" onClick={onBack}>
          ← Quay lại
        </button>
        <h1>🅿️ Quản Lý Vị Trí Trống</h1>
        <div className="header-controls">
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto refresh
          </label>
          
          {autoRefresh && (
            <>
              <select 
                value={autoRefreshInterval} 
                onChange={(e) => setAutoRefreshInterval(Number(e.target.value))}
                className="interval-select"
              >
                <option value={1}>1 phút</option>
                <option value={5}>5 phút</option>
                <option value={15}>15 phút</option>
                <option value={30}>30 phút</option>
                <option value={60}>1 giờ</option>
              </select>
              
              <label className="auto-reset-toggle">
                <input
                  type="checkbox"
                  checked={autoResetEnabled}
                  onChange={(e) => setAutoResetEnabled(e.target.checked)}
                />
                Auto reset cảm biến
              </label>
            </>
          )}
        </div>
      </header>

      {message && <div className="message">{message}</div>}

      {slotsData?.success && (
        <div className="summary-cards">
          <div className="summary-card total">
            <h3>📊 Tổng vị trí</h3>
            <div className="number">{slotsData.summary?.total_slots || 0}</div>
          </div>
          <div className="summary-card occupied">
            <h3>🚗 Đã đỗ</h3>
            <div className="number">{slotsData.summary?.occupied || 0}</div>
          </div>
          <div className="summary-card available">
            <h3>⬜ Trống</h3>
            <div className="number">{slotsData.summary?.available || 0}</div>
          </div>
          <div className="summary-card rate">
            <h3>📈 Tỷ lệ lấp đầy</h3>
            <div className="number">{slotsData.summary?.occupancy_rate || 0}%</div>
          </div>
        </div>
      )}

      <div className="controls">
        <button 
          onClick={() => fetchParkingSlots(false)} 
          disabled={loading}
          className="refresh-btn"
        >
          🔄 Làm mới
        </button>
        <button 
          onClick={() => fetchParkingSlots(true)} 
          disabled={loading}
          className="refresh-reset-btn"
        >
          ⚡ Làm mới + Reset
        </button>
        <button 
          onClick={handleResetSensors} 
          disabled={loading}
          className="reset-btn"
        >
          🔧 Reset riêng
        </button>
      </div>

      <div className="parking-area">
        <h2>🏢 Sơ đồ bãi đỗ xe</h2>
        {slotsData?.success ? renderParkingGrid() : (
          <div className="error-state">
            <p>⚠️ ESP32 không phản hồi</p>
            <p>Kiểm tra kết nối và thử lại</p>
          </div>
        )}
      </div>

      {slotsData?.esp32_data && (
        <div className="technical-info">
          <h3>🔧 Thông tin kỹ thuật</h3>
          <div className="info-grid">
            <div>
              <strong>Số IC 74HC595:</strong> {slotsData.esp32_data.soIC}
            </div>
            <div>
              <strong>Tổng cảm biến:</strong> {slotsData.esp32_data.totalSensors}
            </div>
            <div>
              <strong>ESP32 Uptime:</strong> {Math.floor(slotsData.esp32_data.timestamp / 1000)}s
            </div>
            <div>
              <strong>Cập nhật lần cuối:</strong> {
                new Date(slotsData.last_updated).toLocaleString('vi-VN')
              }
            </div>
          </div>
          
          <div className="reset-info">
            <h4>⏰ Cấu hình Auto Refresh/Reset</h4>
            <div className="reset-status">
              <div className="reset-mode auto">
                <span className="status-indicator">🔄</span>
                <div className="reset-details">
                  <strong>Auto Refresh:</strong> {autoRefresh ? `Mỗi ${autoRefreshInterval} phút` : 'Tắt'}
                  <div className="reset-subtitle">
                    {autoRefresh && autoResetEnabled 
                      ? `Tự động làm mới + reset cảm biến mỗi ${autoRefreshInterval} phút`
                      : autoRefresh 
                        ? `Tự động làm mới (không reset) mỗi ${autoRefreshInterval} phút`
                        : 'Chỉ làm mới thủ công'
                    }
                  </div>
                </div>
              </div>
              <div className="reset-mode manual">
                <span className="status-indicator">⚡</span>
                <div className="reset-details">
                  <strong>Manual Control:</strong> 3 tùy chọn
                  <div className="reset-subtitle">
                    🔄 Làm mới • ⚡ Làm mới + Reset • 🔧 Reset riêng
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParkingSlots;