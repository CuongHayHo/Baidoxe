"""
Card Data Model - Model dữ liệu cho thẻ đỗ xe RFID

Chức năng chính:
- Lưu trữ thông tin thẻ RFID và trạng thái xe
- Tính toán thời gian đỗ xe tự động 
- Validation dữ liệu đầu vào
- Chuyển đổi giữa dict và object
- Real-time tracking cho xe đang trong bãi
- Hỗ trợ 3 loại thẻ: resident (cứ dân), temporary (gửi xe tạm), unknown (không xác định)
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json

class Card:
    """
    Lớp ParkingCard - Đại diện cho một thẻ đỗ xe với khả năng tracking thời gian
    
    Attributes:
        uid: Mã định danh duy nhất của thẻ RFID
        status: Trạng thái (0=ngoài bãi, 1=trong bãi)  
        entry_time: Thời gian vào bãi (ISO format)
        exit_time: Thời gian ra bãi (ISO format)
        created_at: Thời gian tạo thẻ lần đầu
        parking_duration: Thời lượng đỗ xe được tính toán
    """
    
    def __init__(self, uid: str, status: int = 0, entry_time: Optional[str] = None, 
                 exit_time: Optional[str] = None, created_at: Optional[str] = None):
        """
        Khởi tạo đối tượng thẻ đỗ xe
        
        Args:
            uid: Mã định danh duy nhất của thẻ RFID
            status: Trạng thái thẻ (0=ngoài bãi, 1=trong bãi)
            entry_time: Timestamp ISO khi xe vào bãi (tùy chọn)
            exit_time: Timestamp ISO khi xe ra bãi (tùy chọn)
            created_at: Timestamp ISO khi tạo thẻ lần đầu (tùy chọn)
        """
        self.uid = uid.upper().strip()  # Chuẩn hóa UID: viết hoa và loại bỏ khoảng trắng
        self.status = status
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.parking_duration = None
        
        # Tính toán thời lượng đỗ xe nếu có đủ thông tin
        self._calculate_parking_duration()
    
    def _calculate_parking_duration(self):
        """
        Tính toán thời lượng đỗ xe
        - Nếu xe đã ra: tính từ entry_time đến exit_time
        - Nếu xe còn trong bãi: tính từ entry_time đến thời điểm hiện tại
        """
        if self.entry_time:
            try:
                entry = datetime.fromisoformat(self.entry_time.replace('Z', '+00:00'))
                
                # If car exited, use exit time; if still inside, use current time
                if self.exit_time and self.status == 0:
                    end_time = datetime.fromisoformat(self.exit_time.replace('Z', '+00:00'))
                elif self.status == 1:
                    # Car is still inside - calculate current duration
                    end_time = datetime.now(timezone.utc)
                else:
                    # No exit time and not inside - can't calculate
                    self.parking_duration = None
                    return
                
                duration = end_time - entry
                total_seconds = int(duration.total_seconds())
                
                # Validate duration is positive
                if total_seconds < 0:
                    # Invalid data - entry time after exit time
                    # Clear invalid exit_time to fix the issue
                    self.exit_time = None
                    self.parking_duration = {
                        "total_seconds": 0,
                        "hours": 0,
                        "minutes": 0,
                        "display": "Dữ liệu lỗi - thời gian không hợp lệ (đã reset)"
                    }
                    return
                
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                
                # Add real-time indicator if still inside
                status_indicator = " (hiện tại)" if self.status == 1 else ""
                
                self.parking_duration = {
                    "total_seconds": total_seconds,
                    "hours": hours,
                    "minutes": minutes,
                    "display": f"{hours} giờ {minutes} phút{status_indicator}" if hours > 0 else f"{minutes} phút{status_indicator}"
                }
            except (ValueError, AttributeError):
                self.parking_duration = None
    
    def update_status(self, new_status: int) -> Dict[str, Any]:
        """
        Update card status with proper time tracking
        
        Args:
            new_status: New status (0=outside, 1=inside)
            
        Returns:
            Dictionary with operation result and details
        """
        old_status = self.status
        current_time = datetime.now(timezone.utc).isoformat()
        
        if new_status == old_status:
            return {
                "success": False,
                "message": f"Thẻ {self.uid} đã ở trạng thái {new_status}",
                "action": "no_change"
            }
        
        self.status = new_status
        
        if new_status == 1:  # Entering parking lot
            self.entry_time = current_time
            self.exit_time = None  # Clear previous exit time
            self.parking_duration = None
            action = "entry"
            message = f"Xe vào bãi - Thẻ {self.uid}"
            
        else:  # Exiting parking lot (new_status == 0)
            self.exit_time = current_time
            self._calculate_parking_duration()
            action = "exit"
            duration_text = self.parking_duration["display"] if self.parking_duration else "N/A"
            message = f"Xe ra khỏi bãi - Thẻ {self.uid} - Thời gian đỗ: {duration_text}"
        
        return {
            "success": True,
            "message": message,
            "action": action,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": current_time,
            "parking_duration": self.parking_duration
        }
    
    def refresh_parking_duration(self):
        """Refresh parking duration for cars currently inside (real-time update)"""
        if self.status == 1 and self.entry_time:
            self._calculate_parking_duration()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for JSON serialization"""
        result = {
            "uid": self.uid,
            "status": self.status,
            "created_at": self.created_at
        }
        
        if self.entry_time:
            result["entry_time"] = self.entry_time
        if self.exit_time:
            result["exit_time"] = self.exit_time
        if self.parking_duration:
            result["parking_duration"] = self.parking_duration
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingCard':
        """Create ParkingCard instance from dictionary"""
        return cls(
            uid=data["uid"],
            status=data.get("status", 0),
            entry_time=data.get("entry_time"),
            exit_time=data.get("exit_time"),
            created_at=data.get("created_at")
        )
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate card data
        
        Returns:
            Dictionary with validation result
        """
        errors = []
        
        # UID validation
        if not self.uid or len(self.uid.strip()) == 0:
            errors.append("UID không được để trống")
        elif len(self.uid) < 4:
            errors.append("UID phải có ít nhất 4 ký tự")
        
        # Status validation  
        if self.status not in [0, 1]:
            errors.append("Status phải là 0 (ngoài bãi) hoặc 1 (trong bãi)")
        
        # Time validation
        if self.entry_time:
            try:
                datetime.fromisoformat(self.entry_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("Entry time không đúng định dạng ISO")
        
        if self.exit_time:
            try:
                datetime.fromisoformat(self.exit_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("Exit time không đúng định dạng ISO")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def __str__(self):
        status_text = "TRONG BÃI" if self.status == 1 else "NGOÀI BÃI"
        return f"Card({self.uid}, {status_text})"
    
    def __repr__(self):
        return f"ParkingCard(uid='{self.uid}', status={self.status})"