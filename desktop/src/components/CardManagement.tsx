/**
 * CardManagement.tsx - Quản lý thẻ xe
 * 
 * Chức năng:
 * - Xem danh sách tất cả thẻ xe
 * - Thêm thẻ mới với đầy đủ thông tin
 * - Xóa thẻ
 * - Tìm kiếm/Filter thẻ
 * - Xem chi tiết thẻ
 */

import React, { useState, useEffect } from 'react';
import { useNotifications } from './Notifications';
import parkingApi from '../api';
import '../styles/CardManagement.css';

interface Card {
  id: string;
  owner_name?: string;
  owner_phone?: string;
  status: number;
  created_at?: string;
  updated_at?: string;
}

const CardManagement: React.FC = () => {
  const [cards, setCards] = useState<Card[]>([]);
  const [filteredCards, setFilteredCards] = useState<Card[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    uid: '',
    owner_name: '',
    status: 'outside'
  });
  const { showToast } = useNotifications();

  // Lấy danh sách thẻ
  const fetchCards = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/api/cards/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      const data = await response.json();
      
      if (data.cards && Array.isArray(data.cards)) {
        const cardList = data.cards.map((cardData: any) => ({
          id: cardData.uid,
          owner_name: cardData.name || '',
          status: cardData.status || 0,
          created_at: cardData.created_at || '',
          updated_at: cardData.updated_at || ''
        }));
        setCards(cardList);
        setFilteredCards(cardList);
      }
    } catch (error) {
      console.error('Error fetching cards:', error);
      showToast('error', '❌ Lỗi tải dữ liệu', 'Không thể tải danh sách thẻ');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  // Tìm kiếm thẻ
  useEffect(() => {
    const filtered = cards.filter(card =>
      card.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (card.owner_name && card.owner_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (card.owner_phone && card.owner_phone.includes(searchTerm))
    );
    setFilteredCards(filtered);
  }, [searchTerm, cards]);

  // Thêm thẻ mới
  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.uid.trim()) {
      showToast('error', '❌ Thông tin không đầy đủ', 'Vui lòng nhập UID thẻ');
      return;
    }

    if (!formData.owner_name.trim()) {
      showToast('error', '❌ Thông tin không đầy đủ', 'Vui lòng nhập tên chủ thẻ (ít nhất 2 ký tự)');
      return;
    }

    if (formData.owner_name.trim().length < 2) {
      showToast('error', '❌ Thông tin không hợp lệ', 'Tên chủ thẻ phải ít nhất 2 ký tự');
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/api/cards/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          id: formData.uid,
          name: formData.owner_name,
          status: formData.status
        })
      });

      const data = await response.json();

      if (response.ok) {
        showToast('success', '✅ Thêm thẻ thành công', `Thẻ ${formData.uid} đã được thêm vào hệ thống`);
        setFormData({ uid: '', owner_name: '', status: 'outside' });
        setShowAddForm(false);
        fetchCards();
      } else {
        showToast('error', '❌ Thêm thẻ thất bại', data.message || 'Lỗi không xác định');
      }
    } catch (error) {
      console.error('Error adding card:', error);
      showToast('error', '❌ Lỗi kết nối', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  // Xóa thẻ
  const handleDeleteCard = async (uid: string) => {
    if (!window.confirm(`Bạn chắc chắn muốn xóa thẻ ${uid}?`)) {
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`http://localhost:5000/api/cards/${uid}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (response.ok) {
        showToast('success', '✅ Xóa thẻ thành công', `Thẻ ${uid} đã được xóa khỏi hệ thống`);
        fetchCards();
      } else {
        const data = await response.json();
        showToast('error', '❌ Xóa thẻ thất bại', data.message || 'Lỗi không xác định');
      }
    } catch (error) {
      console.error('Error deleting card:', error);
      showToast('error', '❌ Lỗi kết nối', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusLabel = (status: number) => {
    switch (status) {
      case 0:
        return '🚗 Ngoài bãi';
      case 1:
        return '🅿️ Trong bãi';
      default:
        return '❌ Không xác định';
    }
  };

  // Thay đổi trạng thái thẻ (vào/ra bãi)
  const handleChangeStatus = async (uid: string, newStatus: number) => {
    try {
      setIsLoading(true);
      const response = await fetch(`http://localhost:5000/api/cards/${uid}/status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      const data = await response.json();

      if (response.ok) {
        const statusText = newStatus === 1 ? 'vào bãi' : 'ra bãi';
        showToast('success', '✅ Cập nhật trạng thái', `Thẻ ${uid} ${statusText} thành công`);
        fetchCards();
      } else {
        showToast('error', '❌ Cập nhật thất bại', data.message || 'Lỗi không xác định');
      }
    } catch (error) {
      console.error('Error changing status:', error);
      showToast('error', '❌ Lỗi kết nối', 'Không thể kết nối tới server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card-management">
      {/* Header */}
      <div className="card-header">
        <div>
          <h2>🎫 Quản lý Thẻ Xe</h2>
          <p>Tổng cộng: {cards.length} thẻ</p>
        </div>
        <button
          className="btn-add-card"
          onClick={() => setShowAddForm(!showAddForm)}
          disabled={isLoading}
        >
          {showAddForm ? '✕ Đóng' : '➕ Thêm Thẻ Mới'}
        </button>
      </div>

      {/* Add Card Form */}
      {showAddForm && (
        <div className="add-card-form">
          <h3>📝 Thêm Thẻ Xe Mới</h3>
          <form onSubmit={handleAddCard}>
            <div className="form-group">
              <label>UID Thẻ *</label>
              <input
                type="text"
                value={formData.uid}
                onChange={(e) => setFormData({...formData, uid: e.target.value})}
                placeholder="Nhập UID thẻ (16 ký tự hex)"
                required
              />
            </div>

            <div className="form-group">
              <label>Tên Chủ Xe *</label>
              <input
                type="text"
                value={formData.owner_name}
                onChange={(e) => setFormData({...formData, owner_name: e.target.value})}
                placeholder="Nhập tên chủ xe (ít nhất 2 ký tự)"
                required
              />
            </div>

            <div className="form-group">
              <label>Trạng Thái</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({...formData, status: e.target.value})}
              >
                <option value="outside">🚗 Ngoài bãi</option>
                <option value="inside">🅿️ Trong bãi</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-confirm" disabled={isLoading}>
                {isLoading ? '⏳ Đang xử lý...' : '✅ Thêm Thẻ'}
              </button>
              <button
                type="button"
                className="btn-cancel"
                onClick={() => setShowAddForm(false)}
                disabled={isLoading}
              >
                ✕ Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search Bar */}
      <div className="card-search">
        <input
          type="text"
          placeholder="🔍 Tìm kiếm theo UID, tên chủ xe hoặc số điện thoại..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Cards List */}
      <div className="cards-list">
        {isLoading && <div className="loading">⏳ Đang tải...</div>}

        {!isLoading && filteredCards.length === 0 && (
          <div className="empty-state">
            <p>😕 Không tìm thấy thẻ nào</p>
          </div>
        )}

        {!isLoading && filteredCards.length > 0 && (
          <div className="cards-grid">
            {filteredCards.map((card) => (
              <div key={card.id} className="card-item">
                <div className="card-content">
                  <div className="card-uid">
                    <strong>🆔 {card.id}</strong>
                  </div>

                  <div className="card-info">
                    {card.owner_name && (
                      <div className="info-row">
                        <span className="label">👤 Chủ xe:</span>
                        <span className="value">{card.owner_name}</span>
                      </div>
                    )}

                    {card.owner_phone && (
                      <div className="info-row">
                        <span className="label">📱 SĐT:</span>
                        <span className="value">{card.owner_phone}</span>
                      </div>
                    )}

                    <div className="info-row">
                      <span className="label">📊 Trạng thái:</span>
                      <span className="status-badge">
                        {getStatusLabel(card.status)}
                      </span>
                    </div>

                    {card.created_at && (
                      <div className="info-row small">
                        <span className="label">📅 Tạo:</span>
                        <span className="value">
                          {new Date(card.created_at).toLocaleString('vi-VN')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="card-actions">
                  {card.status === 0 ? (
                    <button
                      className="btn-status btn-enter"
                      onClick={() => handleChangeStatus(card.id, 1)}
                      disabled={isLoading}
                      title="Xe vào bãi"
                    >
                      📥 Vào Bãi
                    </button>
                  ) : (
                    <button
                      className="btn-status btn-exit"
                      onClick={() => handleChangeStatus(card.id, 0)}
                      disabled={isLoading}
                      title="Xe ra bãi"
                    >
                      📤 Ra Bãi
                    </button>
                  )}
                  <button
                    className="btn-delete"
                    onClick={() => handleDeleteCard(card.id)}
                    disabled={isLoading}
                    title="Xóa thẻ"
                  >
                    🗑️ Xóa
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CardManagement;
