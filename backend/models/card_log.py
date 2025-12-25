"""
CardLog Data Model - Model dữ liệu cho log thẻ RFID

Chức năng chính:
- Lưu trữ log các lần quét thẻ và hành động tương ứng
- Tracking thời gian và chi tiết từng lần quét
- Hỗ trợ lưu metadata và details bổ sung
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

class CardLog:
    """
    CardLog - Đại diện cho một bản ghi log của thẻ RFID
    
    Attributes:
        id: UUID định danh duy nhất cho log entry
        timestamp: Thời gian quét thẻ (ISO format)
        card_id: Mã ID của thẻ RFID
        action: Loại hành động (entry, exit, scan, unknown)
        details: Dict chứa thông tin bổ sung (source, local_time, etc)
        metadata: Dict chứa metadata khác
    """
    
    def __init__(self, card_id: str, action: str, timestamp: Optional[str] = None, 
                 id: Optional[str] = None, details: Optional[Dict[str, Any]] = None, 
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Khởi tạo một log entry cho thẻ RFID
        
        Args:
            card_id: Mã ID của thẻ RFID
            action: Loại hành động (entry, exit, scan, unknown, etc)
            timestamp: Timestamp ISO khi quét (mặc định = thời điểm hiện tại)
            id: UUID cho log entry (mặc định = tạo mới)
            details: Dict thông tin bổ sung
            metadata: Dict metadata
        """
        self.id = id or str(uuid.uuid4())  # Tự tạo UUID nếu không có
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.card_id = card_id  # Đổi từ card_number
        self.action = action  # entry, exit, scan, unknown, etc
        self.details = details or {}  # Extra info (source, local_time, etc)
        self.metadata = metadata or {}  # Additional metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert CardLog object to dictionary (cho serialization)
        
        Returns:
            Dictionary với đầy đủ thông tin
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "card_id": self.card_id,
            "action": self.action,
            "details": self.details,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CardLog':
        """
        Tạo CardLog object từ dictionary
        
        Args:
            data: Dictionary chứa log data
            
        Returns:
            CardLog instance
        """
        return cls(
            card_id=data.get('card_id'),
            action=data.get('action'),
            timestamp=data.get('timestamp'),
            id=data.get('id'),
            details=data.get('details'),
            metadata=data.get('metadata')
        )
    
    def __repr__(self):
        return f"<CardLog {self.card_id} {self.action} {self.timestamp}>"
