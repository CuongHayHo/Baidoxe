/**
 * CardList.tsx - Component hiển thị danh sách tất cả thẻ đỗ xe
 * Chức năng: Render list thẻ với thông tin chi tiết và nút xóa
 */

import React from 'react';
import { ParkingCard } from '../types';

/**
 * Props interface cho CardList component
 */
interface CardListProps {
  /** Object chứa tất cả thẻ (key = UID, value = ParkingCard) */
  cards: Record<string, ParkingCard>;
  /** Callback function để xóa thẻ */
  onDeleteCard: (uid: string) => void;
}

/**
 * CardList Component
 * Hiển thị danh sách thẻ với thông tin chi tiết và actions
 */
const CardList: React.FC<CardListProps> = ({ cards, onDeleteCard }) => {
  
  // ================== PAGINATION STATE ==================
  const [currentPage, setCurrentPage] = React.useState(1);
  const itemsPerPage = 10; // Hiển thị 10 thẻ mỗi trang
  
  // ================== UTILITY FUNCTIONS ==================
  
  /**
   * Format thời gian từ ISO string sang format hiển thị
   * @param timeStr - ISO time string hoặc undefined
   * @returns Formatted time string hoặc dash nếu không có
   */
  const formatTime = (timeStr?: string) => {
    if (!timeStr) return '-';
    try {
      // Sử dụng locale Vietnam để format time
      return new Date(timeStr).toLocaleString('vi-VN');
    } catch {
      // Fallback nếu parse failed
      return timeStr;
    }
  };

  /**
   * Tạo status badge với styling phù hợp
   * @param status - Status code (0=ngoài bãi, 1=trong bãi)
   * @returns JSX element với badge styling
   */
  const getStatusBadge = (status: number) => {
    if (status === 1) {
      return (
        <span className="status-badge status-inside">
          🅿️ TRONG BÃI
        </span>
      );
    } else {
      return (
        <span className="status-badge status-outside">
          🚗 NGOÀI BÃI
        </span>
      );
    }
  };

  // ================== DATA PROCESSING ==================
  
  /** Convert object sang array để dễ map và render */
  const cardEntries = Object.entries(cards);
  
  /** Pagination calculations */
  const totalItems = cardEntries.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentCards = cardEntries.slice(startIndex, endIndex);

  // ================== CONDITIONAL RENDERING ==================
  
  /** Hiển thị message nếu không có thẻ nào */
  if (cardEntries.length === 0) {
    return (
      <div className="card-list">
        <p className="no-cards">Chưa có thẻ nào trong hệ thống</p>
      </div>
    );
  }

  // ================== MAIN RENDER ==================
  return (
    <div className="card-list">
      {/* Header với count và pagination info */}
      <div className="list-header">
        <h3>Danh sách thẻ ({totalItems})</h3>
        {totalPages > 1 && (
          <span className="pagination-info">
            Trang {currentPage}/{totalPages} (hiển thị {startIndex + 1}-{Math.min(endIndex, totalItems)} trong {totalItems})
          </span>
        )}
      </div>
      
      {/* Render từng thẻ */}
      {currentCards.map(([uid, card]) => (
        <div 
          key={uid} 
          className={`card-item ${card.status === 1 ? 'inside' : 'outside'}`}
        >
          {/* Card Header: UID + Status Badge */}
          <div className="card-header">
            <strong className="card-uid">🏷️ {uid}</strong>
            {getStatusBadge(card.status)}
          </div>
          
          {/* Card Details: Duration + Times */}
          <div className="card-details">
            {/* Hiển thị thời gian đỗ nếu xe đang trong bãi */}
            {card.status === 1 && card.parking_duration && (
              <div className="parking-duration">
                ⏱️ Thời gian đỗ: <strong>{card.parking_duration.display}</strong>
              </div>
            )}
            
            {/* Thông tin thời gian vào/ra */}
            <div className="time-info">
              {card.entry_time && (
                <div>📥 Vào: {formatTime(card.entry_time)}</div>
              )}
              {card.exit_time && (
                <div>📤 Ra: {formatTime(card.exit_time)}</div>
              )}
            </div>
          </div>
          
          {/* Delete Button */}
          <button 
            className="delete-btn"
            onClick={() => onDeleteCard(uid)}
            title="Xóa thẻ"
          >
            🗑️ Xóa
          </button>
        </div>
      ))}
      
      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="pagination-controls">
          <button 
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            ⏮️ Đầu
          </button>
          
          <button 
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            ⬅️ Trước
          </button>
          
          <span className="pagination-current">
            {currentPage} / {totalPages}
          </span>
          
          <button 
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Tiếp ➡️
          </button>
          
          <button 
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Cuối ⏭️
          </button>
        </div>
      )}
    </div>
  );
};

export default CardList;