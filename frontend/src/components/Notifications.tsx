/**
 * Notifications System - Hệ thống toast notifications và activity monitoring
 * 
 * Chức năng chính:
 * - Toast notifications với các loại: success/error/warning/info
 * - Real-time activity monitoring (unknown cards, status changes)
 * - Statistics change detection và auto-refresh
 * - Context provider cho toàn bộ app
 * - Auto-dismiss với customizable duration
 * - Queue management cho multiple notifications
 */

import React, { useState, useEffect, useCallback } from 'react';

/**
 * Interface cho toast notification
 */
interface Toast {
  id: string;                                        // ID duy nhất của toast
  type: 'success' | 'error' | 'warning' | 'info';   // Loại notification
  title: string;                                     // Tiêu đề toast
  message: string;                                   // Nội dung chi tiết
  timestamp: Date;                                   // Thời gian tạo
  duration?: number;                                 // Thời gian hiển thị (ms)
}

/**
 * Interface cho Notification Context
 */
interface NotificationContextType {
  showToast: (type: Toast['type'], title: string, message: string, duration?: number) => void;
  clearToasts: () => void;
}

// Tạo React Context cho notification system
const NotificationContext = React.createContext<NotificationContextType | null>(null);

/**
 * Hook để sử dụng notification system trong components
 * @returns NotificationContextType với showToast và clearToasts methods
 * @throws Error nếu được sử dụng ngoài NotificationProvider
 */
export const useNotifications = () => {
  const context = React.useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications phải được sử dụng bên trong NotificationProvider');
  }
  return context;
};

/**
 * Props interface cho NotificationProvider component
 */
interface NotificationProviderProps {
  children: React.ReactNode; // Child components sẽ có access đến notification context
}

/**
 * NotificationProvider Component - Context provider cho notification system
 * Wraps toàn bộ app để provide toast notifications và monitoring
 */
export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  // State lưu trữ danh sách toast notifications hiện tại
  const [toasts, setToasts] = useState<Toast[]>([]);

  /**
   * Function tạo và hiển thị toast notification
   * @param type - Loại notification (success/error/warning/info)
   * @param title - Tiêu đề ngắn gọn
   * @param message - Nội dung chi tiết
   * @param duration - Thời gian hiển thị (ms), 0 = không tự động ẩn
   */
  const showToast = useCallback((type: Toast['type'], title: string, message: string, duration = 5000) => {
    // Tạo ID duy nhất cho toast (timestamp + random string)
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newToast: Toast = {
      id,
      type,
      title,
      message,
      timestamp: new Date(),
      duration
    };

    // Thêm toast mới vào danh sách (hiển thị ở cuối)
    setToasts(prev => [...prev, newToast]);

    // Tự động xóa toast sau khoảng thời gian duration
    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
      }, duration);
    }
  }, []);

  /**
   * Function xóa tất cả toast notifications
   */
  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  /**
   * Function xóa một toast cụ thể theo ID
   * @param id - ID của toast cần xóa
   */
  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  /**
   * Function lấy icon phù hợp cho từng loại toast
   * @param type - Loại toast notification
   * @returns Emoji icon tương ứng
   */
  const getToastIcon = (type: Toast['type']) => {
    switch (type) {
      case 'success': return '✅';  // Thành công
      case 'error': return '❌';    // Lỗi
      case 'warning': return '⚠️';  // Cảnh báo
      case 'info': return 'ℹ️';     // Thông tin
      default: return '📢';         // Mặc định
    }
  };

  // Context value chứa các methods để child components sử dụng
  const value = {
    showToast,
    clearToasts
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      
      {/* === TOAST CONTAINER === */}
      {/* Container chứa tất cả toast notifications, position fixed ở góc màn hình */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div 
            key={toast.id} 
            className={`toast toast-${toast.type}`}
            onClick={() => removeToast(toast.id)} // Click để đóng toast
          >
            {/* Icon hiển thị loại notification */}
            <div className="toast-icon">
              {getToastIcon(toast.type)}
            </div>
            
            {/* Nội dung chính của toast */}
            <div className="toast-content">
              <div className="toast-title">{toast.title}</div>
              <div className="toast-message">{toast.message}</div>
              <div className="toast-timestamp">
                {toast.timestamp.toLocaleTimeString('vi-VN')}
              </div>
            </div>
            
            {/* Nút đóng toast */}
            <button 
              className="toast-close"
              onClick={(e) => {
                e.stopPropagation(); // Prevent triggering parent onClick
                removeToast(toast.id);
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

/**
 * === REAL-TIME ACTIVITY MONITOR HOOK ===
 * Hook monitor hoạt động real-time của hệ thống
 * Tự động kiểm tra log mới và hiển thị notifications
 */
export const useActivityMonitor = () => {
  const { showToast } = useNotifications();
  // Lưu số lượng log lần check cuối để detect log mới
  const [lastLogCount, setLastLogCount] = useState(0);

  /**
   * Function kiểm tra hoạt động mới trong hệ thống
   * Gọi API để lấy log mới nhất và so sánh với lần check trước
   */
  const checkForNewActivity = async () => {
    try {
      // Lấy log entry mới nhất (limit=1) để check count
      const response = await fetch('/api/cards/logs?limit=1');
      if (response.ok) {
        const data = await response.json();
        
        // Kiểm tra có log mới không (count tăng so với lần trước)
        if (data.success && data.count > lastLogCount && lastLogCount > 0) {
          // Phát hiện hoạt động mới
          const newCount = data.count - lastLogCount;
          
          if (data.logs && data.logs.length > 0) {
            const latestLog = data.logs[0];
            let title = '';
            let message = '';
            let type: Toast['type'] = 'info';

            // Parse loại hoạt động và tạo notification phù hợp
            switch (latestLog.action) {
              case 'entry':
                title = '🚗 Xe vào bãi';
                message = `Thẻ ${latestLog.card_id} vừa vào bãi đỗ xe`;
                type = 'success';
                break;
              case 'exit':
                title = '🚗 Xe ra khỏi bãi';
                message = `Thẻ ${latestLog.card_id} vừa rời khỏi bãi đỗ xe`;
                type = 'info';
                break;
              case 'scan':
                title = '📱 Quét thẻ';
                message = `Thẻ ${latestLog.card_id} được quét bởi hệ thống`;
                type = 'info';
                break;
              case 'unknown':
                title = '❓ Thẻ không xác định';
                message = `Phát hiện thẻ lạ: ${latestLog.card_id}`;
                type = 'warning';
                break;
              default:
                title = '📝 Hoạt động mới';
                message = `Thẻ ${latestLog.card_id}: ${latestLog.action}`;
                type = 'info';
            }

            // Hiển thị toast notification với thông tin chi tiết
            showToast(type, title, message);
          } else {
            // Fallback nếu không có log chi tiết
            showToast('info', '🔔 Hoạt động mới', `Có ${newCount} hoạt động mới`);
          }
        }
        
        // Cập nhật count để sử dụng cho lần check tiếp theo
        setLastLogCount(data.count || 0);
      }
    } catch (error) {
      console.error('Lỗi khi kiểm tra hoạt động mới:', error);
    }
  };

  useEffect(() => {
    // Khởi tạo log count lần đầu
    checkForNewActivity();

    // Kiểm tra hoạt động mới mỗi 10 giây
    const interval = setInterval(checkForNewActivity, 10000);

    // Cleanup interval khi component unmount
    return () => clearInterval(interval);
  }, [lastLogCount, showToast]);

  return { checkForNewActivity };
};

/**
 * === REAL-TIME STATS MONITOR HOOK ===
 * Hook monitor thống kê hệ thống real-time
 * Phát hiện thay đổi quan trọng trong stats và cảnh báo
 */
export const useStatsMonitor = () => {
  const { showToast } = useNotifications();
  // Lưu stats lần check trước để so sánh
  const [previousStats, setPreviousStats] = useState<any>(null);

  /**
   * Function kiểm tra thay đổi trong thống kê hệ thống
   * So sánh stats hiện tại với lần check trước để phát hiện thay đổi quan trọng
   */
  const checkStatsChange = async () => {
    try {
      const response = await fetch('/api/cards/statistics');
      if (response.ok) {
        const data = await response.json();
        const stats = data.statistics || data;

        if (previousStats) {
          // Kiểm tra thay đổi quan trọng trong số xe trong bãi
          if (stats.inside_parking !== previousStats.inside_parking) {
            const change = stats.inside_parking - previousStats.inside_parking;
            if (change > 0) {
              // Có xe mới vào bãi
              showToast('success', '📈 Tăng số xe', `Có thêm ${change} xe vào bãi. Tổng: ${stats.inside_parking}/${stats.total_cards}`);
            } else {
              // Có xe rời bãi
              showToast('info', '📉 Giảm số xe', `Có ${Math.abs(change)} xe rời bãi. Tổng: ${stats.inside_parking}/${stats.total_cards}`);
            }
          }

          // Kiểm tra cảnh báo tỷ lệ sử dụng bãi xe
          if (stats.occupancy_rate >= 90 && previousStats.occupancy_rate < 90) {
            showToast('warning', '⚠️ Bãi xe gần đầy', `Tỷ lệ sử dụng: ${stats.occupancy_rate.toFixed(1)}%`);
          }

          // Cảnh báo bãi xe đầy
          if (stats.occupancy_rate === 100 && previousStats.occupancy_rate < 100) {
            showToast('error', '🚫 Bãi xe đầy', 'Không còn chỗ trống trong bãi xe');
          }
        }

        // Lưu stats hiện tại để so sánh cho lần tiếp theo
        setPreviousStats(stats);
      }
    } catch (error) {
      console.error('Lỗi khi kiểm tra thống kê:', error);
    }
  };

  useEffect(() => {
    // Khởi tạo stats lần đầu
    checkStatsChange();

    // Kiểm tra thay đổi stats mỗi 30 giây
    const interval = setInterval(checkStatsChange, 30000);

    // Cleanup interval khi component unmount
    return () => clearInterval(interval);
  }, []); // Bỏ previousStats khỏi dependency để tránh infinite loop

  return { checkStatsChange };
};

export default NotificationProvider;