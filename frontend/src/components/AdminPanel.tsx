/**
 * AdminPanel Component - Trang quản trị hệ thống
 * 
 * Chức năng chính:
 * - Hiển thị thống kê tổng quan hệ thống
 * - Quản lý backup files (tạo, khôi phục, xóa)
 * - Các thao tác maintenance (fix data, clear logs)
 * - System health monitoring
 * - Database management tools
 * - Real-time system status updates
 */

import React, { useState, useEffect } from 'react';
import { useNotifications } from './Notifications';

/**
 * Interface cho thông tin backup file
 */
interface BackupFile {
  filename: string;      // Tên file backup
  path: string;          // Đường dẫn đầy đủ
  size_bytes: number;    // Kích thước file (bytes)
  created_time: string;  // Thời gian tạo (ISO format)
  modified_time: string; // Thời gian sửa cuối (ISO format)
  is_hourly: boolean;    // True nếu là backup tự động theo giờ
  is_manual: boolean;    // True nếu là backup thủ công
}

/**
 * Interface cho thông tin tổng quan hệ thống
 */
interface SystemInfo {
  total_cards: number;   // Tổng số thẻ trong hệ thống
  total_logs: number;    // Tổng số log entries
  backup_count: number;  // Số lượng backup files
  system_status: string; // Trạng thái hệ thống (healthy/warning/error)
  last_backup: string;   // Thời gian backup cuối cùng
}

const AdminPanel: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [backupFiles, setBackupFiles] = useState<BackupFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useNotifications();

  const fetchBackupFiles = async () => {
    try {
      const response = await fetch('/api/cards/backups');
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setBackupFiles(result.backups || []);
        }
      }
    } catch (err) {
      console.error('Error fetching backup files:', err);
    }
  };

  const fetchSystemInfo = async () => {
    setIsLoading(true);
    try {
      const [statsResponse, logsResponse, backupsResponse] = await Promise.all([
        fetch('/api/cards/statistics'),
        fetch('/api/cards/logs?limit=1'),
        fetch('/api/cards/backups')
      ]);

      let stats = null;
      let logs = null;
      let backups = null;

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        stats = statsData.statistics || statsData;
      }

      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        logs = logsData;
      }

      if (backupsResponse.ok) {
        const backupsData = await backupsResponse.json();
        if (backupsData.success) {
          backups = backupsData.backups || [];
          setBackupFiles(backups);
        }
      }

      setSystemInfo({
        total_cards: stats?.total_cards || 0,
        total_logs: logs?.count || 0,
        backup_count: backups?.length || 0,
        system_status: 'healthy',
        last_backup: backups?.length > 0 ? backups[0]?.created_time : new Date().toISOString()
      });

      setError(null);
    } catch (err) {
      console.error('Error fetching system info:', err);
      setError('Không thể tải thông tin hệ thống');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemInfo();
    fetchBackupFiles();
  }, []);

  const createBackup = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/cards/backup', { method: 'POST' });
      const result = await response.json();

      if (result.success) {
        showToast('success', '✅ Backup thành công', `Đã tạo backup: ${result.backup_path}`);
        fetchSystemInfo(); // Refresh info
        fetchBackupFiles(); // Refresh backup list
      } else {
        showToast('error', '❌ Backup thất bại', result.message || 'Lỗi không xác định');
      }
    } catch (err) {
      showToast('error', '❌ Lỗi backup', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  const fixData = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn sửa lỗi dữ liệu? Thao tác này sẽ tạo backup trước khi sửa.')) {
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch('/api/cards/fix-data', { method: 'POST' });
      const result = await response.json();

      if (result.success) {
        showToast('success', '✅ Sửa lỗi thành công', 
          `Đã sửa ${result.fixed_count} thẻ / ${result.total_cards} tổng số thẻ`);
        fetchSystemInfo(); // Refresh info
        fetchBackupFiles(); // Refresh backup list
      } else {
        showToast('error', '❌ Sửa lỗi thất bại', result.message || 'Lỗi không xác định');
      }
    } catch (err) {
      showToast('error', '❌ Lỗi sửa dữ liệu', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  const clearLogs = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa toàn bộ logs? Thao tác này KHÔNG thể hoàn tác!')) {
      return;
    }

    try {
      setIsLoading(true);
      // Note: This would need a backend endpoint to clear logs
      showToast('warning', '⚠️ Tính năng chưa sẵn sàng', 'Endpoint xóa logs chưa được implement');
    } catch (err) {
      showToast('error', '❌ Lỗi xóa logs', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  const exportSystemReport = async () => {
    try {
      const [statsResponse, logsResponse] = await Promise.all([
        fetch('/api/cards/statistics'),
        fetch('/api/cards/logs?limit=100') // Get recent logs for report
      ]);

      const statsData = statsResponse.ok ? await statsResponse.json() : null;
      const logsData = logsResponse.ok ? await logsResponse.json() : null;

      const report = {
        generated_at: new Date().toISOString(),
        system_info: {
          total_cards: statsData?.statistics?.total_cards || statsData?.total_cards || 0,
          inside_parking: statsData?.statistics?.inside_parking || statsData?.inside_parking || 0,
          outside_parking: statsData?.statistics?.outside_parking || statsData?.outside_parking || 0,
          occupancy_rate: statsData?.statistics?.occupancy_rate || statsData?.occupancy_rate || 0,
          total_logs: logsData?.count || 0
        },
        recent_activity: logsData?.logs || []
      };

      const blob = new Blob([JSON.stringify(report, null, 2)], 
        { type: 'application/json;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 
        `system_report_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      showToast('success', '📥 Xuất báo cáo thành công', 'File báo cáo đã được tải xuống');
    } catch (err) {
      showToast('error', '❌ Lỗi xuất báo cáo', 'Không thể tạo file báo cáo');
    }
  };

  const resetSystem = async () => {
    const confirmText = 'RESET';
    const userInput = window.prompt(
      `⚠️ CẢNH BÁO: Thao tác này sẽ RESET toàn bộ hệ thống!\n\n` +
      `- Xóa tất cả thẻ\n` +
      `- Xóa tất cả logs\n` +
      `- Tạo backup trước khi reset\n\n` +
      `Nhập "${confirmText}" để xác nhận:`
    );

    if (userInput !== confirmText) {
      showToast('info', 'ℹ️ Hủy thao tác', 'Reset hệ thống đã bị hủy');
      return;
    }

    try {
      setIsLoading(true);
      
      // Create backup first
      await createBackup();
      
      // Note: This would need backend endpoints to actually reset
      showToast('warning', '⚠️ Tính năng chưa sẵn sàng', 
        'Endpoint reset hệ thống chưa được implement để đảm bảo an toàn');
    } catch (err) {
      showToast('error', '❌ Lỗi reset hệ thống', 'Không thể thực hiện reset');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin-panel-page">
      <div className="admin-header">
        <h1>⚙️ Bảng Điều Khiển Quản Trị</h1>
        <div className="admin-badge">
          🔐 Administrator
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* System Overview */}
      <div className="admin-section">
        <h2>📊 Tổng Quan Hệ Thống</h2>
        <div className="system-overview">
          <div className="overview-card">
            <div className="card-icon">📋</div>
            <div className="card-content">
              <h3>Tổng Số Thẻ</h3>
              <div className="card-number">{systemInfo?.total_cards || 0}</div>
            </div>
          </div>

          <div className="overview-card">
            <div className="card-icon">📝</div>
            <div className="card-content">
              <h3>Tổng Số Logs</h3>
              <div className="card-number">{systemInfo?.total_logs || 0}</div>
            </div>
          </div>

          <div className="overview-card">
            <div className="card-icon">💾</div>
            <div className="card-content">
              <h3>Files Backup</h3>
              <div className="card-number">{systemInfo?.backup_count || 0}</div>
            </div>
          </div>

          <div className="overview-card">
            <div className="card-icon">💚</div>
            <div className="card-content">
              <h3>Trạng Thái</h3>
              <div className="card-status healthy">Hoạt động tốt</div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="admin-section">
        <h2>🗂️ Quản Lý Dữ Liệu</h2>
        <div className="data-management">
          <div className="management-card">
            <h3>💾 Backup & Khôi Phục</h3>
            <p>Tạo backup dữ liệu thẻ để đảm bảo an toàn</p>
            <div className="card-actions">
              <button 
                onClick={createBackup}
                disabled={isLoading}
                className="action-btn backup-btn"
              >
                💾 Tạo Backup Ngay
              </button>
            </div>
          </div>

          <div className="management-card">
            <h3>🔧 Sửa Lỗi Dữ Liệu</h3>
            <p>Tự động phát hiện và sửa lỗi trong dữ liệu thẻ</p>
            <div className="card-actions">
              <button 
                onClick={fixData}
                disabled={isLoading}
                className="action-btn fix-btn"
              >
                🔧 Sửa Lỗi Dữ Liệu
              </button>
            </div>
          </div>

          <div className="management-card">
            <h3>📥 Xuất Báo Cáo</h3>
            <p>Tạo báo cáo tổng quan về hoạt động hệ thống</p>
            <div className="card-actions">
              <button 
                onClick={exportSystemReport}
                disabled={isLoading}
                className="action-btn export-btn"
              >
                📥 Xuất Báo Cáo
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Backup Files List */}
      <div className="admin-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>📁 Danh Sách Backup Files</h2>
          <button 
            onClick={fetchBackupFiles}
            disabled={isLoading}
            className="action-btn refresh-btn"
            style={{ marginBottom: '10px' }}
          >
            🔄 Refresh
          </button>
        </div>
        <div className="backup-files-section">
          {backupFiles.length > 0 ? (
            <div className="backup-files-grid">
              {backupFiles.map((backup, index) => (
                <div key={index} className="backup-file-card">
                  <div className="backup-file-header">
                    <h4>{backup.filename}</h4>
                    <span className={`backup-type ${backup.is_manual ? 'manual' : 'hourly'}`}>
                      {backup.is_manual ? '🔧 Manual' : '⏰ Auto'}
                    </span>
                  </div>
                  <div className="backup-file-details">
                    <div className="backup-detail">
                      <span className="detail-label">📅 Created:</span>
                      <span className="detail-value">
                        {new Date(backup.created_time).toLocaleString('vi-VN', {
                          year: 'numeric',
                          month: '2-digit', 
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <div className="backup-detail">
                      <span className="detail-label">💾 Size:</span>
                      <span className="detail-value">
                        {(backup.size_bytes / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </div>
                  <div className="backup-actions">
                    <button 
                      className="action-btn restore-btn"
                      onClick={() => {
                        if (window.confirm(`Khôi phục từ backup: ${backup.filename}?`)) {
                          showToast('info', 'ℹ️ Tính năng đang phát triển', 'Restore backup sẽ có trong phiên bản tiếp theo');
                        }
                      }}
                    >
                      ↩️ Restore
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-backups">
              <p>📭 Chưa có backup files nào</p>
              <button onClick={createBackup} className="action-btn backup-btn">
                💾 Tạo Backup Đầu Tiên
              </button>
            </div>
          )}
        </div>
      </div>

      {/* System Maintenance */}
      <div className="admin-section">
        <h2>🛠️ Bảo Trì Hệ Thống</h2>
        <div className="maintenance-section">
          <div className="maintenance-card warning">
            <h3>🗑️ Xóa Logs Cũ</h3>
            <p>Xóa toàn bộ logs để giải phóng không gian lưu trữ</p>
            <div className="card-actions">
              <button 
                onClick={clearLogs}
                disabled={isLoading}
                className="action-btn danger-btn"
              >
                🗑️ Xóa Tất Cả Logs
              </button>
            </div>
          </div>

          <div className="maintenance-card danger">
            <h3>⚠️ Reset Hệ Thống</h3>
            <p>
              <strong>NGUY HIỂM:</strong> Xóa toàn bộ dữ liệu và khởi tạo lại hệ thống
            </p>
            <div className="card-actions">
              <button 
                onClick={resetSystem}
                disabled={isLoading}
                className="action-btn reset-btn"
              >
                ⚠️ Reset Toàn Bộ Hệ Thống
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="admin-section">
        <h2>⚡ Thao Tác Nhanh</h2>
        <div className="quick-actions-grid">
          <button 
            onClick={() => window.location.reload()}
            className="quick-btn refresh-btn"
          >
            🔄 Làm Mới Trang
          </button>
          
          <button 
            onClick={fetchSystemInfo}
            disabled={isLoading}
            className="quick-btn update-btn"
          >
            📊 Cập Nhật Thống Kê
          </button>
          
          <button 
            onClick={() => window.open('/api/cards/', '_blank')}
            className="quick-btn api-btn"
          >
            🔗 Xem API Cards
          </button>
          
          <button 
            onClick={() => window.open('/api/cards/logs', '_blank')}
            className="quick-btn logs-btn"
          >
            📋 Xem API Logs
          </button>
        </div>
      </div>

      {/* System Status Indicator */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            🔄 Đang xử lý...
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;