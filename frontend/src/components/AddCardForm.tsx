/**
 * AddCardForm.tsx - Component form để thêm thẻ đỗ xe mới vào hệ thống
 * Chức năng: Nhập UID thẻ và trạng thái ban đầu, submit để tạo thẻ mới
 */

import React, { useState } from 'react';

/**
 * Props interface cho AddCardForm component
 */
interface AddCardFormProps {
  /** Callback function được gọi khi user submit form thêm thẻ */
  onAddCard: (uid: string, status: number) => void;
}

/**
 * AddCardForm Component
 * Render form để user nhập thông tin thẻ mới và submit
 */
const AddCardForm: React.FC<AddCardFormProps> = ({ onAddCard }) => {
  // ================== LOCAL STATE ==================
  
  /** UID của thẻ mới (input từ user) */
  const [uid, setUid] = useState('');
  
  /** Trạng thái ban đầu của thẻ (0=ngoài bãi, 1=trong bãi) */
  const [status, setStatus] = useState(0);

  // ================== EVENT HANDLERS ==================
  
  /**
   * Xử lý submit form
   * - Prevent default form submission
   * - Validate UID không empty
   * - Normalize UID (trim + uppercase)
   * - Call callback với data
   * - Reset form về trạng thái ban đầu
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Prevent page reload
    
    if (uid.trim()) {
      // Normalize UID: remove whitespace và convert uppercase
      onAddCard(uid.trim().toUpperCase(), status);
      
      // Reset form sau khi submit thành công
      setUid('');
      setStatus(0);
    }
  };

  // ================== RENDER ==================
  return (
    <form className="add-card-form" onSubmit={handleSubmit}>
      <h3>Thêm thẻ mới</h3>
      
      {/* UID Input Field */}
      <div className="form-group">
        <label htmlFor="uid">UID Thẻ:</label>
        <input
          type="text"
          id="uid"
          value={uid}
          onChange={(e) => setUid(e.target.value)}
          placeholder="Nhập UID thẻ"
          required
        />
      </div>
      
      {/* Status Selection Dropdown */}
      <div className="form-group">
        <label htmlFor="status">Trạng thái ban đầu:</label>
        <select
          id="status"
          value={status}
          onChange={(e) => setStatus(parseInt(e.target.value))}
        >
          <option value={0}>🚗 Ngoài bãi</option>
          <option value={1}>🅿️ Trong bãi</option>
        </select>
      </div>
      
      {/* Submit Button */}
      <button type="submit" className="add-btn">
        ➕ Thêm thẻ
      </button>
    </form>
  );
};

export default AddCardForm;