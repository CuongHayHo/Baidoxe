/**
 * UnknownCardNotification.tsx - Component hiển thị thông báo thẻ lạ
 * Chức năng: Hiển thị thẻ được UNO R4 WiFi detect nhưng chưa có trong database
 * Cho phép user thêm thẻ với trạng thái phù hợp hoặc bỏ qua
 */

import React from 'react';
import { parkingApi } from '../api';

/**
 * Interface định nghĩa cấu trúc của một thẻ lạ
 */
interface UnknownCard {
  uid: string;                    // UID của thẻ RFID
  timestamp: string;              // Thời gian phát hiện (ISO format)
  ip?: string;                    // IP của device phát hiện (optional)
  type?: string;                  // Loại device (UNO-R4, ESP32, etc.)
  direction?: string;             // Hướng quét (IN/OUT/unknown)
  gate_location?: string;         // Vị trí cổng (IN Gate, OUT Gate)
  suggested_status?: number;      // Trạng thái gợi ý (0=ngoài, 1=trong)
  auto_suggestion?: string;       // Text gợi ý tự động từ hệ thống
}

/**
 * Props interface cho UnknownCardNotification component
 */
interface UnknownCardNotificationProps {
  /** Danh sách thẻ lạ cần hiển thị */
  unknownCards: UnknownCard[];
  /** Callback để thêm thẻ vào hệ thống */
  onAddCard: (uid: string, status: number) => Promise<void>;
  /** Callback để refresh danh sách thẻ lạ */
  onRefresh: () => void;
}

/**
 * UnknownCardNotification Component
 * Hiển thị notification banner với danh sách thẻ lạ và actions
 */
const UnknownCardNotification: React.FC<UnknownCardNotificationProps> = ({
  unknownCards,
  onAddCard,
  onRefresh
}) => {
  
  // ================== EVENT HANDLERS ==================
  
  /**
   * Xử lý thêm thẻ lạ vào hệ thống
   * @param uid - UID của thẻ cần thêm
   * @param suggestedStatus - Trạng thái gợi ý (optional)
   */
  const handleAddCard = async (uid: string, suggestedStatus?: number) => {
    const status = suggestedStatus !== undefined ? suggestedStatus : 0;
    const statusText = status === 0 ? 'NGOÀI BÃI (0)' : 'TRONG BÃI (1)';
    
    // Xác nhận với user trước khi thêm
    const shouldAdd = window.confirm(
      `🆔 Phát hiện thẻ mới: ${uid}\n\n` +
      `Bạn có muốn thêm thẻ này vào hệ thống?\n\n` +
      `• Trạng thái: ${statusText}\n` +
      `• Lần quét tiếp theo sẽ ${status === 0 ? 'mở barrier VÀO' : 'mở barrier RA'}`
    );

    if (shouldAdd) {
      try {
        // Thêm thẻ vào hệ thống
        await onAddCard(uid, status);
        // Xóa thẻ khỏi danh sách unknown
        await parkingApi.removeUnknownCard(uid);
        // Refresh danh sách
        onRefresh();
      } catch (error) {
        console.error('Failed to add unknown card:', error);
        alert(`❌ Lỗi thêm thẻ: ${error}`);
      }
    }
  };

  /**
   * Lấy thông tin hiển thị cho direction badge
   * @param card - UnknownCard object
   * @returns Object chứa badge text, location và className
   */
  const getDirectionInfo = (card: UnknownCard) => {
    if (card.direction === 'IN') {
      return {
        badge: '🚪 VÀO',
        location: card.gate_location || 'IN Gate',
        className: 'direction-in'
      };
    } else if (card.direction === 'OUT') {
      return {
        badge: '🚪 RA', 
        location: card.gate_location || 'OUT Gate',
        className: 'direction-out'
      };
    }
    return {
      badge: '❓ Không xác định',
      location: 'Unknown',
      className: 'direction-unknown'
    };
  };

  /**
   * Lấy text hiển thị cho suggested status
   * @param status - Status code (0 hoặc 1)
   * @returns Formatted status text với icon
   */
  const getSuggestedStatusText = (status: number) => {
    return status === 0 ? '🟦 NGOÀI BÃI (0)' : '🟩 TRONG BÃI (1)';
  };

  /**
   * Xử lý bỏ qua thẻ lạ (xóa khỏi danh sách thông báo)
   * @param uid - UID của thẻ cần bỏ qua
   */
  const handleIgnoreCard = async (uid: string) => {
    const shouldIgnore = window.confirm(
      `🚫 Bỏ qua thẻ: ${uid}\n\n` +
      `Thẻ này sẽ được xóa khỏi danh sách thông báo.\n` +
      `Nếu thẻ được quét lại, thông báo sẽ xuất hiện lại.`
    );

    if (shouldIgnore) {
      try {
        await parkingApi.removeUnknownCard(uid);
        onRefresh();
      } catch (error) {
        console.error('Failed to ignore unknown card:', error);
      }
    }
  };

  // ================== UTILITY FUNCTIONS ==================
  
  /**
   * Format timestamp thành định dạng hiển thị
   * @param timestamp - ISO timestamp string
   * @returns Formatted datetime string (Vietnamese locale)
   */
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',  
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // ================== CONDITIONAL RENDERING ==================
  
  /** Không hiển thị gì nếu không có thẻ lạ */
  if (unknownCards.length === 0) {
    return null;
  }

  // ================== MAIN RENDER ==================
  return (
    <div className="unknown-cards-notification">
      {/* Header với title và clear all button */}
      <div className="notification-header">
        <h3>🆔 Thẻ mới phát hiện ({unknownCards.length})</h3>
        <button 
          className="clear-all-btn"
          onClick={async () => {
            if (window.confirm('Xóa tất cả thông báo thẻ mới?')) {
              await parkingApi.clearUnknownCards();
              onRefresh();
            }
          }}
        >
          Xóa tất cả
        </button>
      </div>
      
      {/* Danh sách thẻ lạ */}
      <div className="unknown-cards-list">
        {unknownCards.map((card, index) => {
          const dirInfo = getDirectionInfo(card);
          return (
            <div key={`${card.uid}-${index}`} className="unknown-card-item">
              {/* Card Header: UID + Direction + Time */}
              <div className="unknown-card-header">
                <div className="unknown-card-uid">
                  <strong>🆔 {card.uid}</strong>
                </div>
                <div className={`direction-badge ${dirInfo.className}`}>
                  {dirInfo.badge} ({dirInfo.location})
                </div>
                <div className="unknown-card-time">
                  ⏰ {formatTimestamp(card.timestamp)}
                </div>
              </div>
              
              {/* Auto suggestion nếu có */}
              {card.auto_suggestion && (
                <div className="auto-suggestion">
                  💡 {card.auto_suggestion}
                </div>
              )}
              
              {/* Action buttons */}
              <div className="unknown-card-actions">
                {/* Thêm với status = 0 (ngoài bãi) */}
                <button 
                  className="add-unknown-btn add-outside"
                  onClick={() => handleAddCard(card.uid, 0)}
                  title="Thêm thẻ với trạng thái NGOÀI BÃI"
                >
                  ➕ {getSuggestedStatusText(0)}
                </button>
                
                {/* Thêm với status = 1 (trong bãi) */}
                <button 
                  className="add-unknown-btn add-inside"
                  onClick={() => handleAddCard(card.uid, 1)}
                  title="Thêm thẻ với trạng thái TRONG BÃI"
                >
                  ➕ {getSuggestedStatusText(1)}
                </button>
                
                {/* Button gợi ý nếu có suggested_status */}
                {card.suggested_status !== undefined && (
                  <button 
                    className={`add-unknown-btn suggested ${card.suggested_status === 0 ? 'add-outside' : 'add-inside'}`}
                    onClick={() => handleAddCard(card.uid, card.suggested_status)}
                    title={`Thêm với trạng thái gợi ý dựa trên vị trí quét`}
                  >
                    ⭐ GỢI Ý: {getSuggestedStatusText(card.suggested_status!)}
                  </button>
                )}
                
                {/* Button bỏ qua */}
                <button 
                  className="ignore-unknown-btn"
                  onClick={() => handleIgnoreCard(card.uid)}
                  title="Bỏ qua thông báo này"
                >
                  🚫 Bỏ qua
                </button>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Summary statistics */}
      <div className="notification-summary">
        <p>
          📊 Tổng: {unknownCards.length} | 
          🚪 VÀO: {unknownCards.filter(c => c.direction === 'IN').length} | 
          🚪 RA: {unknownCards.filter(c => c.direction === 'OUT').length}
        </p>
      </div>
    </div>
  );
};

export default UnknownCardNotification;