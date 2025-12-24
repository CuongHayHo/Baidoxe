"""
Parking slot data model for ESP32 sensor data
Định nghĩa cấu trúc dữ liệu cho parking slots từ ESP32
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class ParkingSlot:
    """
    Individual parking slot representation
    """
    
    def __init__(self, slot_id: int, status: int, last_updated: Optional[str] = None):
        """
        Initialize a parking slot
        
        Args:
            slot_id: Slot number (1-6)
            status: Slot status (0=available, 1=occupied) 
            last_updated: ISO timestamp of last sensor reading
        """
        self.slot_id = slot_id
        self.status = status  # 0 = available, 1 = occupied
        self.last_updated = last_updated or datetime.now(timezone.utc).isoformat()
    
    def update_status(self, new_status: int) -> bool:
        """
        Update slot status
        
        Args:
            new_status: New status (0=available, 1=occupied)
            
        Returns:
            True if status changed, False if no change
        """
        if self.status != new_status:
            self.status = new_status
            self.last_updated = datetime.now(timezone.utc).isoformat()
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if slot is available"""
        return self.status == 0
    
    def is_occupied(self) -> bool:
        """Check if slot is occupied"""
        return self.status == 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "slot_id": self.slot_id,
            "status": self.status,
            "available": self.is_available(),
            "occupied": self.is_occupied(),
            "last_updated": self.last_updated
        }

class ParkingSlotsData:
    """
    Complete parking slots data from ESP32
    """
    
    def __init__(self, esp32_data: Dict[str, Any]):
        """
        Initialize parking slots data from ESP32 response
        
        Args:
            esp32_data: Raw data from ESP32 API
        """
        self.success = esp32_data.get("success", False)
        self.last_updated = datetime.now(timezone.utc).isoformat()
        self.reset_performed = esp32_data.get("reset_performed", False)
        
        # ESP32 sensor data
        self.esp32_raw = esp32_data.get("esp32_data", {})
        self.total_sensors = self.esp32_raw.get("totalSensors", 6)
        self.ic_count = self.esp32_raw.get("soIC", 1)
        self.esp32_timestamp = self.esp32_raw.get("timestamp", 0)
        
        # Process slot data
        raw_data = self.esp32_raw.get("data", [])
        self.slots = []
        
        for i, status in enumerate(raw_data):
            slot = ParkingSlot(
                slot_id=i + 1,
                status=status,
                last_updated=self.last_updated
            )
            self.slots.append(slot)
        
        # Calculate summary statistics
        self._calculate_summary()
    
    def _calculate_summary(self):
        """Calculate summary statistics"""
        total_slots = len(self.slots)
        occupied_slots = sum(1 for slot in self.slots if slot.is_occupied())
        available_slots = total_slots - occupied_slots
        
        occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
        
        self.summary = {
            "total_slots": total_slots,
            "occupied": occupied_slots,
            "available": available_slots,
            "occupancy_rate": round(occupancy_rate, 1)
        }
    
    def get_slot(self, slot_id: int) -> Optional[ParkingSlot]:
        """
        Get specific slot by ID
        
        Args:
            slot_id: Slot ID (1-6)
            
        Returns:
            ParkingSlot instance or None if not found
        """
        for slot in self.slots:
            if slot.slot_id == slot_id:
                return slot
        return None
    
    def get_available_slots(self) -> List[ParkingSlot]:
        """Get list of available slots"""
        return [slot for slot in self.slots if slot.is_available()]
    
    def get_occupied_slots(self) -> List[ParkingSlot]:
        """Get list of occupied slots"""
        return [slot for slot in self.slots if slot.is_occupied()]
    
    def update_slot_status(self, slot_id: int, new_status: int) -> bool:
        """
        Update specific slot status
        
        Args:
            slot_id: Slot ID (1-6)
            new_status: New status (0=available, 1=occupied)
            
        Returns:
            True if status was updated, False if slot not found or no change
        """
        slot = self.get_slot(slot_id)
        if slot and slot.update_status(new_status):
            self._calculate_summary()  # Recalculate summary
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON API response"""
        return {
            "success": self.success,
            "esp32_data": {
                "soIC": self.ic_count,
                "totalSensors": self.total_sensors,
                "timestamp": self.esp32_timestamp,
                "data": [slot.status for slot in self.slots]
            },
            "summary": self.summary,
            "slots": [slot.to_dict() for slot in self.slots],
            "last_updated": self.last_updated,
            "reset_performed": self.reset_performed
        }
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate parking slots data
        
        Returns:
            Dictionary with validation result
        """
        errors = []
        
        # Check if we have any slots
        if len(self.slots) == 0:
            errors.append("Không có dữ liệu slot nào")
        
        # Validate slot count
        if len(self.slots) != self.total_sensors:
            errors.append(f"Số lượng slots ({len(self.slots)}) không khớp với totalSensors ({self.total_sensors})")
        
        # Validate each slot
        for slot in self.slots:
            if slot.status not in [0, 1]:
                errors.append(f"Slot {slot.slot_id} có status không hợp lệ: {slot.status}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "slots_count": len(self.slots),
            "expected_count": self.total_sensors
        }
    
    def __str__(self):
        available = self.summary["available"] 
        occupied = self.summary["occupied"]
        return f"ParkingSlots({available} available, {occupied} occupied)"
    
    def __repr__(self):
        return f"ParkingSlotsData(slots={len(self.slots)}, success={self.success})"