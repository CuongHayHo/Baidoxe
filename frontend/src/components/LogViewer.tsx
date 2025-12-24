/**
 * LogViewer Component - Hiển thị nhật ký hoạt động hệ thống
 * 
 * Chức năng chính:
 * - Hiển thị danh sách log hoạt động với pagination
 * - Filter theo action type và card ID
 * - Real-time loading và error handling
 * - Export log data và clear filters
 * - Responsive design cho mobile và desktop
 */

import React, { useState, useEffect } from 'react';
import { parkingApi } from '../api';

/**
 * Interface cho một log entry từ backend
 */
interface LogEntry {
  id: string;          // ID duy nhất của log entry
  timestamp: string;   // Thời gian thực hiện (ISO format)
  card_id: string;     // ID thẻ thực hiện hành động
  action: string;      // Loại hành động (entry/exit/scan/unknown/etc)
  details: any;        // Chi tiết bổ sung của hành động
  metadata?: any;      // Metadata tùy chọn
}

/**
 * Interface cho response từ API logs với pagination
 */
interface LogResponse {
  success: boolean;           // Trạng thái thành công của request
  count: number;              // Tổng số log entries (sau filter)
  page_count: number;         // Số lượng entries trong response này
  has_more: boolean;          // Còn log entries khác không
  logs: LogEntry[];           // Mảng log entries
  filters: {                  // Filters đã áp dụng
    action: string;
    card_id: string;
    limit: number;
    offset: number;
  };
}

const LogViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  // Filter states
  const [filters, setFilters] = useState({
    action: '',
    card_id: '',
    limit: 50,
    offset: 0
  });

  // Available filter options
  const actionOptions = [
    { value: '', label: 'Tất cả hành động' },
    { value: 'entry', label: 'Vào bãi' },
    { value: 'exit', label: 'Ra khỏi bãi' },
    { value: 'scan', label: 'Quét thẻ' },
    { value: 'unknown', label: 'Thẻ lạ' },
    { value: 'created', label: 'Tạo thẻ' },
    { value: 'deleted', label: 'Xóa thẻ' },
    { value: 'updated', label: 'Cập nhật thẻ' }
  ];

  const fetchLogs = async (newFilters = filters) => {
    setIsLoading(true);
    setError(null);
    
    // Clear previous logs to prevent append behavior
    setLogs([]);

    try {
      const data: LogResponse = await parkingApi.getLogs({
        action: newFilters.action || undefined,
        card_id: newFilters.card_id || undefined,
        limit: newFilters.limit,
        offset: newFilters.offset
      });
      
      if (data.success) {
        console.log('📄 LogViewer: Received', data.logs?.length, 'logs, offset:', newFilters.offset);
        console.log('📊 LogViewer: Total count:', data.count, 'Has more:', data.has_more);
        setLogs(data.logs || []);
        setTotalCount(data.count || 0);
      } else {
        throw new Error('API returned error');
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Không thể tải dữ liệu log');
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleFilterChange = (key: string, value: string | number) => {
    const newFilters = { ...filters, [key]: value, offset: 0 };
    setFilters(newFilters);
    fetchLogs(newFilters);
  };

  const handlePageChange = (newOffset: number) => {
    console.log('🔄 LogViewer: Page change to offset:', newOffset);
    const newFilters = { ...filters, offset: newOffset };
    setFilters(newFilters);
    fetchLogs(newFilters);
  };

  const clearFilters = () => {
    const newFilters = { action: '', card_id: '', limit: 50, offset: 0 };
    setFilters(newFilters);
    fetchLogs(newFilters);
  };

  const getActionBadge = (action: string) => {
    const badges = {
      entry: { text: 'Vào bãi', class: 'badge-entry', icon: '🚗➡️' },
      exit: { text: 'Ra khỏi bãi', class: 'badge-exit', icon: '🚗⬅️' },
      scan: { text: 'Quét thẻ', class: 'badge-scan', icon: '📱' },
      unknown: { text: 'Thẻ lạ', class: 'badge-unknown', icon: '❓' },
      created: { text: 'Tạo thẻ', class: 'badge-created', icon: '➕' },
      deleted: { text: 'Xóa thẻ', class: 'badge-deleted', icon: '🗑️' },
      updated: { text: 'Cập nhật', class: 'badge-updated', icon: '✏️' }
    };

    const badge = badges[action as keyof typeof badges] || 
      { text: action, class: 'badge-default', icon: '📝' };

    return (
      <span className={`log-badge ${badge.class}`}>
        {badge.icon} {badge.text}
      </span>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString('vi-VN'),
      time: date.toLocaleTimeString('vi-VN')
    };
  };

  const formatDetails = (details: any) => {
    if (!details || typeof details !== 'object') return null;

    return (
      <div className="log-details">
        {details.source && (
          <span className="detail-tag">Nguồn: {details.source}</span>
        )}
        {details.previous_status !== undefined && details.new_status !== undefined && (
          <span className="detail-tag">
            Trạng thái: {details.previous_status} → {details.new_status}
          </span>
        )}
        {details.local_time && (
          <span className="detail-tag">Thời gian: {details.local_time}</span>
        )}
      </div>
    );
  };

  const exportLogs = async () => {
    try {
      const data = await parkingApi.getLogs({
        action: filters.action || undefined,
        card_id: filters.card_id || undefined,
        limit: 1000, // Export more records
        offset: 0
      });

      if (data.success && data.logs) {
        // Convert actions to Vietnamese
        const actionMap = {
          'entry': 'Vào bãi',
          'exit': 'Ra khỏi bãi', 
          'scan': 'Quét thẻ',
          'unknown': 'Thẻ lạ'
        };

        const csvRows = [
          'Thời gian,Mã thẻ,Hành động,Chi tiết'
        ];

        data.logs.forEach((log: LogEntry) => {
          const { date, time } = formatTimestamp(log.timestamp);
          const action = actionMap[log.action as keyof typeof actionMap] || log.action;
          
          // Format details properly
          let details = '';
          if (log.details) {
            if (log.details.source) details += `Nguồn: ${log.details.source}; `;
            if (log.details.previous_status !== undefined && log.details.new_status !== undefined) {
              details += `Trạng thái: ${log.details.previous_status} → ${log.details.new_status}; `;
            }
            if (log.details.local_time) details += `Thời gian: ${log.details.local_time}`;
          }

          // Escape commas and quotes in CSV
          const escapeCsv = (str: string) => {
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
              return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
          };

          csvRows.push([
            escapeCsv(`${date} ${time}`),
            escapeCsv(log.card_id),
            escapeCsv(action),
            escapeCsv(details)
          ].join(','));
        });

        const csvContent = csvRows.join('\n');
        
        // Use UTF-8 BOM and proper MIME type for Excel compatibility
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { 
          type: 'text/csv;charset=utf-8' 
        });
        
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `parking_logs_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      alert('Lỗi xuất file: ' + err);
    }
  };

  const totalPages = Math.ceil(totalCount / filters.limit);
  const currentPage = Math.floor(filters.offset / filters.limit) + 1;

  return (
    <div className="log-viewer-page">
      <div className="log-header">
        <h1>📋 Nhật Ký Hoạt Động</h1>
        <div className="log-summary">
          Tổng cộng: <strong>{totalCount}</strong> bản ghi
        </div>
      </div>

      {/* Filters */}
      <div className="log-filters">
        <div className="filter-row">
          <div className="filter-group">
            <label>Hành động:</label>
            <select 
              value={filters.action} 
              onChange={(e) => handleFilterChange('action', e.target.value)}
            >
              {actionOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Mã thẻ:</label>
            <input 
              type="text" 
              placeholder="Nhập mã thẻ..."
              value={filters.card_id}
              onChange={(e) => handleFilterChange('card_id', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>Số bản ghi:</label>
            <select 
              value={filters.limit} 
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <div className="filter-actions">
            <button onClick={clearFilters} className="clear-btn">
              🔄 Xóa lọc
            </button>
            <button onClick={() => fetchLogs()} className="refresh-btn">
              🔄 Làm mới
            </button>
            <button onClick={exportLogs} className="export-btn">
              📥 Xuất CSV
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="loading-spinner">
          🔄 Đang tải dữ liệu...
        </div>
      )}

      {/* Logs Table */}
      <div className="logs-container">
        {logs.length > 0 ? (
          <>
            <div className="logs-table">
              {logs.map((log) => {
                const { date, time } = formatTimestamp(log.timestamp);
                
                return (
                  <div key={log.id} className="log-row">
                    <div className="log-time">
                      <div className="log-date">{date}</div>
                      <div className="log-time-value">{time}</div>
                    </div>
                    
                    <div className="log-card">
                      <span className="card-id">{log.card_id}</span>
                    </div>
                    
                    <div className="log-action">
                      {getActionBadge(log.action)}
                    </div>
                    
                    <div className="log-info">
                      {formatDetails(log.details)}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            <div className="pagination">
              <div className="pagination-info">
                Trang {currentPage} / {totalPages} 
                ({filters.offset + 1}-{Math.min(filters.offset + filters.limit, totalCount)} / {totalCount})
              </div>
              
              <div className="pagination-controls">
                <button 
                  onClick={() => handlePageChange(0)}
                  disabled={isLoading || filters.offset === 0}
                  className="page-btn"
                >
                  ⏮️ Đầu
                </button>
                
                <button 
                  onClick={() => handlePageChange(Math.max(0, filters.offset - filters.limit))}
                  disabled={isLoading || filters.offset === 0}
                  className="page-btn"
                >
                  ◀️ Trước
                </button>
                
                <button 
                  onClick={() => handlePageChange(filters.offset + filters.limit)}
                  disabled={isLoading || filters.offset + filters.limit >= totalCount}
                  className="page-btn"
                >
                  ▶️ Sau
                </button>
                
                <button 
                  onClick={() => handlePageChange((totalPages - 1) * filters.limit)}
                  disabled={isLoading || filters.offset + filters.limit >= totalCount}
                  className="page-btn"
                >
                  ⏭️ Cuối
                </button>
              </div>
            </div>
          </>
        ) : (
          !isLoading && (
            <div className="no-logs">
              📝 Không có dữ liệu log nào phù hợp với bộ lọc
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default LogViewer;