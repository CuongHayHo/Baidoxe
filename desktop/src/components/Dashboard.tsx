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

/**
 * Interface định nghĩa cấu trúc dữ liệu log hoạt động
 * - count: Tổng số log
 * - logs: Mảng các log gần đây với thông tin chi tiết
 */
interface LogStats {
  count: number;
  logs: Array<{
    id: string;        // ID duy nhất của log
    timestamp: string; // Thời gian thực hiện hành động
    card_id: string;   // ID của thẻ thực hiện hành động
    action: string;    // Loại hành động (entry/exit/scan/unknown)
    details: any;      // Thông tin chi tiết khác
  }>;
}

const Dashboard: React.FC = () => {
  // === STATE MANAGEMENT ===
  // Lưu trữ dữ liệu thống kê từ API
  const [stats, setStats] = useState<DashboardStats | null>(null);
  // Lưu trữ danh sách log hoạt động gần đây
  const [recentLogs, setRecentLogs] = useState<LogStats | null>(null);
  // Trạng thái loading khi đang fetch dữ liệu
  const [isLoading, setIsLoading] = useState(true);
  // Lưu trữ thông báo lỗi nếu có
  const [error, setError] = useState<string | null>(null);
  // Thời gian cập nhật cuối cùng để hiển thị cho user
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  /**
   * Hàm lấy base URL cho API calls
   */
  const getApiBaseUrl = () => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:5000';
    }
    return `http://${window.location.hostname}:5000`;
  };

  /**
   * Hàm fetch dữ liệu dashboard từ API
   * - Gọi đồng thời 2 API: thống kê và log gần đây
   * - Xử lý lỗi và cập nhật state tương ứng
   * - Cập nhật thời gian fetch cuối cùng
   */
  const fetchStats = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      // Gọi đồng thời 2 API để tối ưu tốc độ loading
      const [statsResponse, logsResponse] = await Promise.all([
        fetch(`${baseUrl}/api/cards/statistics`),    // API lấy thống kê tổng quan
        fetch(`${baseUrl}/api/cards/logs?limit=10`)  // API lấy 10 log gần đây nhất
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

  /**
   * Hàm trả về màu sắc tương ứng với từng loại hành động
   * - entry (vào bãi): xanh lá (success)
   * - exit (ra bãi): đỏ (danger) 
   * - scan (quét thẻ): xanh dương (info)
   * - unknown (thẻ lạ): vàng (warning)
   */
  const getActionColor = (action: string) => {
    switch (action) {
      case 'entry': return '#28a745';   // Bootstrap success color
      case 'exit': return '#dc3545';    // Bootstrap danger color
      case 'scan': return '#007bff';    // Bootstrap primary color
      case 'unknown': return '#ffc107'; // Bootstrap warning color
      default: return '#6c757d';        // Bootstrap secondary color
    }
  };

  /**
   * Hàm trả về icon emoji tương ứng với từng loại hành động
   * Giúp user dễ dàng nhận biết loại hoạt động
   */
  const getActionIcon = (action: string) => {
    switch (action) {
      case 'entry': return '🚗➡️';  // Xe vào
      case 'exit': return '🚗⬅️';   // Xe ra
      case 'scan': return '📱';     // Quét thẻ
      case 'unknown': return '❓';  // Thẻ lạ
      default: return '📝';         // Hành động khác
    }
  };

  /**
   * Hàm format thời gian từ string ISO sang định dạng Việt Nam
   * VD: "2024-01-01T10:30:00Z" → "01/01/2024, 17:30:00"
   */
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('vi-VN');
  };

  // === LOADING STATE ===
  // Hiển thị loading spinner khi đang fetch dữ liệu lần đầu
  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="loading">Đang tải dữ liệu dashboard...</div>
      </div>
    );
  }

  // === MAIN RENDER ===
  return (
    <div className="dashboard-page">
      {/* === HEADER SECTION === */}
      {/* Tiêu đề và các controls như nút refresh, thời gian cập nhật */}
      <div className="dashboard-header">
        <h1>📊 Dashboard Thống Kê</h1>
        <div className="dashboard-controls">
          {/* Nút refresh thủ công - disabled khi đang loading */}
          <button onClick={fetchStats} className="refresh-btn" disabled={isLoading}>
            🔄 Làm mới
          </button>
          {/* Hiển thị thời gian cập nhật cuối */}
          <div className="last-update">
            Cập nhật lần cuối: {lastUpdate.toLocaleTimeString('vi-VN')}
          </div>
        </div>
      </div>

      {/* === ERROR MESSAGE === */}
      {/* Hiển thị thông báo lỗi nếu có */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* === STATISTICS CARDS SECTION === */}
      {/* Grid 4 thẻ hiển thị các thống kê chính */}
      <div className="stats-grid">
        {/* Thẻ 1: Tổng số thẻ trong hệ thống */}
        <div className="stat-card total">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>Tổng Số Thẻ</h3>
            {/* Sử dụng optional chaining và fallback để tránh lỗi */}
            <div className="stat-number">{stats?.total_cards || 0}</div>
          </div>
        </div>

        {/* Thẻ 2: Số xe đang trong bãi */}
        <div className="stat-card inside">
          <div className="stat-icon">🚗</div>
          <div className="stat-content">
            <h3>Xe Trong Bãi</h3>
            <div className="stat-number">{stats?.inside_parking || 0}</div>
          </div>
        </div>

        {/* Thẻ 3: Số xe đang ở ngoài bãi */}
        <div className="stat-card outside">
          <div className="stat-icon">🏠</div>
          <div className="stat-content">
            <h3>Xe Ngoài Bãi</h3>
            <div className="stat-number">{stats?.outside_parking || 0}</div>
          </div>
        </div>

        {/* Thẻ 4: Tỷ lệ sử dụng bãi xe (%) */}
        <div className="stat-card occupancy">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Tỷ Lệ Sử Dụng</h3>
            {/* Format số thập phân 1 chữ số sau dấu phẩy */}
            <div className="stat-number">{stats?.occupancy_rate?.toFixed(1) || 0}%</div>
          </div>
        </div>
      </div>

      {/* === VISUAL OCCUPANCY BAR SECTION === */}
      {/* Progress bar trực quan hiển thị tỷ lệ sử dụng bãi xe */}
      <div className="occupancy-bar-container">
        <h3>Tình Trạng Sử Dụng Bãi Xe</h3>
        {/* Container thanh progress */}
        <div className="occupancy-bar">
          {/* Thanh fill với width động theo tỷ lệ sử dụng */}
          <div 
            className="occupancy-fill" 
            style={{ width: `${stats?.occupancy_rate || 0}%` }}
          ></div>
        </div>
        {/* Label chỉ thị 2 đầu: Trống và Đầy */}
        <div className="occupancy-labels">
          <span>Trống</span>
          <span>Đầy</span>
        </div>
      </div>

      {/* === RECENT ACTIVITY SECTION === */}
      {/* Hiển thị danh sách 10 hoạt động gần đây nhất */}
      <div className="recent-activity">
        <h3>🕒 Hoạt Động Gần Đây</h3>
        {/* Kiểm tra có dữ liệu log không */}
        {recentLogs && recentLogs.logs && recentLogs.logs.length > 0 ? (
          <div className="activity-list">
            {/* Map qua từng log để render */}
            {recentLogs.logs.map((log) => (
              <div key={log.id} className="activity-item">
                {/* Icon hành động */}
                <div className="activity-icon">
                  {getActionIcon(log.action)}
                </div>
                {/* Nội dung chính */}
                <div className="activity-content">
                  {/* Dòng chính: ID thẻ và loại hành động */}
                  <div className="activity-main">
                    <strong>Thẻ {log.card_id}</strong>
                    <span 
                      className="activity-action"
                      style={{ color: getActionColor(log.action) }}
                    >
                      {/* Mapping action sang tiếng Việt */}
                      {log.action === 'entry' && 'vào bãi'}
                      {log.action === 'exit' && 'ra khỏi bãi'}
                      {log.action === 'scan' && 'được quét'}
                      {log.action === 'unknown' && 'thẻ lạ'}
                      {/* Fallback cho action không xác định */}
                      {!['entry', 'exit', 'scan', 'unknown'].includes(log.action) && log.action}
                    </span>
                  </div>
                  {/* Dòng phụ: Thời gian thực hiện */}
                  <div className="activity-time">
                    {formatTimestamp(log.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Hiển thị khi không có hoạt động nào */
          <div className="no-activity">
            Chưa có hoạt động nào được ghi lại
          </div>
        )}
      </div>

      {/* === QUICK ACTIONS SECTION === */}
      {/* Các nút thao tác nhanh để admin thực hiện các tác vụ quan trọng */}
      <div className="quick-actions">
        <h3>⚡ Thao Tác Nhanh</h3>
        <div className="action-buttons">
          {/* Nút tạo backup dữ liệu */}
          <button 
            className="action-btn backup-btn"
            onClick={async () => {
              try {
                const baseUrl = getApiBaseUrl();
                // Gọi API backup dữ liệu
                const response = await fetch(`${baseUrl}/api/cards/backup`, { method: 'POST' });
                const result = await response.json();
                
                // Hiển thị kết quả cho user
                if (result.success) {
                  alert('✅ Backup thành công!');
                } else {
                  alert('❌ Backup thất bại: ' + result.message);
                }
              } catch (err) {
                // Xử lý lỗi network hoặc server
                alert('❌ Lỗi khi backup: ' + err);
              }
            }}
          >
            💾 Tạo Backup
          </button>
          
          {/* Nút sửa lỗi dữ liệu */}
          <button 
            className="action-btn fix-btn"
            onClick={async () => {
              // Xác nhận trước khi thực hiện để tránh thao tác nhầm
              if (window.confirm('Bạn có muốn sửa lỗi dữ liệu không?')) {
                try {
                  const baseUrl = getApiBaseUrl();
                  // Gọi API sửa lỗi dữ liệu
                  const response = await fetch(`${baseUrl}/api/cards/fix-data`, { method: 'POST' });
                  const result = await response.json();
                  
                  if (result.success) {
                    // Hiển thị số lượng thẻ đã sửa và refresh data
                    alert(`✅ Đã sửa ${result.fixed_count} thẻ!`);
                    fetchStats(); // Refresh lại dashboard để cập nhật thống kê
                  } else {
                    alert('❌ Sửa lỗi thất bại: ' + result.message);
                  }
                } catch (err) {
                  // Xử lý lỗi network hoặc server
                  alert('❌ Lỗi khi sửa dữ liệu: ' + err);
                }
              }
            }}
          >
            🔧 Sửa Lỗi Dữ Liệu
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;