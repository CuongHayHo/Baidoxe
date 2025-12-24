"""
ESP32 Service - Logic nghiệp vụ cho giao tiếp với cảm biến ESP32

Chức năng chính:
- Giao tiếp với ESP32 qua HTTP API
- Lấy dữ liệu cảm biến siêu âm để phát hiện xe
- Phân tích và kiểm tra dữ liệu từ ESP32  
- Xử lý lỗi và logic retry
- Giám sát thời gian thực và kiểm tra sức khỏe
"""
import requests
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from models.parking_slot import ParkingSlotsData
from config.config import (
    ESP32_IP, ESP32_PORT, ESP32_TIMEOUT, DETECTION_THRESHOLD
)

logger = logging.getLogger(__name__)

class ESP32Service:
    """
    Lớp service xử lý giao tiếp với ESP32 và quản lý dữ liệu cảm biến
    
    Attributes:
        base_url: URL của ESP32 thật
        timeout: Thời gian chờ cho HTTP requests
        last_data: Dữ liệu cảm biến lần cuối  
        last_updated: Thời gian cập nhật cuối
        detection_threshold: Ngưỡng phát hiện xe (cm)
    """
    
    def __init__(self):
        """Khởi tạo ESP32 service với cấu hình từ config"""
        self.base_url = f"http://{ESP32_IP}:{ESP32_PORT}"
        logger.info(f"� ESP32Service: Kết nối tới ESP32 tại {self.base_url}")
            
        self.timeout = ESP32_TIMEOUT
        self.last_data = None
        self.last_updated = None
        self.detection_threshold = DETECTION_THRESHOLD
    
    def get_parking_slots(self, force_reset: bool = False) -> Tuple[bool, Dict[str, Any], Optional[ParkingSlotsData]]:
        """
        Lấy dữ liệu vị trí đỗ xe từ ESP32
        
        Args:
            force_reset: True nếu muốn reset cảm biến trước khi đọc
            
        Returns:
            Tuple (success, raw_response, parsed_data)
        """
        try:
            # Handle reset request separately
            if force_reset:
                logger.info("Force reset requested - calling ESP32 /detect first")
                reset_success, reset_message = self.reset_sensors()
                if not reset_success:
                    logger.warning(f"Reset failed, continuing with data fetch: {reset_message}")
            
            # Get data from ESP32 (always use /data endpoint)
            url = f"{self.base_url}/data"
            logger.info(f"Fetching ESP32 data from: {url}")
            
            # Make request to ESP32
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Validate response structure
            if "data" not in raw_data:
                logger.error("ESP32 response missing 'data' field")
                return False, raw_data, None
            
            # Add metadata
            processed_data = {
                "success": True,
                "esp32_data": {
                    "soIC": raw_data.get("soIC", 1),
                    "totalSensors": raw_data.get("totalSensors", 6),
                    "timestamp": raw_data.get("timestamp", 0),
                    "data": raw_data["data"]
                },
                "reset_performed": force_reset and raw_data.get("success", False),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            # Create parking slots data object
            slots_data = ParkingSlotsData(processed_data)
            
            # Validate data
            validation = slots_data.validate()
            if not validation["valid"]:
                logger.warning(f"ESP32 data validation failed: {validation['errors']}")
            
            # Cache successful response
            self.last_data = slots_data
            self.last_updated = processed_data["last_updated"]
            
            logger.info(f"Successfully retrieved ESP32 data: {len(slots_data.slots)} slots")
            return True, processed_data, slots_data
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to ESP32 at {self.base_url}")
            error_response = {
                "success": False,
                "error": "ESP32 connection failed",
                "message": "Không thể kết nối với ESP32",
                "esp32_url": self.base_url,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            return False, error_response, None
            
        except requests.exceptions.Timeout:
            logger.error(f"ESP32 request timeout after {self.timeout}s")
            error_response = {
                "success": False,
                "error": "ESP32 timeout",
                "message": f"ESP32 không phản hồi trong {self.timeout}s",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            return False, error_response, None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"ESP32 HTTP error: {e}")
            error_response = {
                "success": False,
                "error": "ESP32 HTTP error", 
                "message": f"Lỗi HTTP từ ESP32: {e}",
                "status_code": e.response.status_code if e.response else None,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            return False, error_response, None
            
        except Exception as e:
            logger.error(f"Unexpected error communicating with ESP32: {e}")
            error_response = {
                "success": False,
                "error": "Unexpected error",
                "message": f"Lỗi không xác định: {str(e)}",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            return False, error_response, None
    
    def reset_sensors(self) -> Tuple[bool, str]:
        """
        Reset ESP32 sensors via dedicated reset endpoint
        
        Returns:
            Tuple of (success, message)
        """
        try:
            url = f"{self.base_url}/detect"
            logger.info(f"Resetting ESP32 sensors via: {url}")
            
            # Send POST request to reset sensors
            response = requests.post(url, timeout=self.timeout * 2)  # Longer timeout for reset
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success", False):
                message = data.get("message", "ESP32 sensors reset successfully")
                logger.info(f"ESP32 reset successful: {message}")
                return True, message
            else:
                error_msg = data.get("message", "Reset failed")
                logger.error(f"ESP32 reset failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to ESP32 for reset")
            return False, "Không thể kết nối với ESP32 để reset"
            
        except requests.exceptions.Timeout:
            logger.error("ESP32 reset request timeout")
            return False, "ESP32 reset timeout"
            
        except Exception as e:
            logger.error(f"Error resetting ESP32 sensors: {e}")
            return False, f"Lỗi reset ESP32: {str(e)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get ESP32 system status and health check
        
        Returns:
            Dictionary with system status information
        """
        # Try to get basic data to check connection
        success, raw_data, slots_data = self.get_parking_slots(force_reset=False)
        
        status = {
            "esp32_connected": success,
            "esp32_url": self.base_url,
            "last_communication": self.last_updated,
            "timeout_setting": self.timeout
        }
        
        if success and slots_data:
            status.update({
                "total_sensors": slots_data.total_sensors,
                "ic_count": slots_data.ic_count,
                "esp32_uptime_ms": slots_data.esp32_timestamp,
                "data_valid": slots_data.validate()["valid"],
                "summary": slots_data.summary
            })
        else:
            status.update({
                "error": raw_data.get("error", "Unknown error"),
                "message": raw_data.get("message", "ESP32 communication failed")
            })
        
        return status
    
    def get_cached_data(self) -> Optional[ParkingSlotsData]:
        """
        Get last successfully retrieved data (cached)
        
        Returns:
            Last ParkingSlotsData or None if no data cached
        """
        return self.last_data
    
    def is_connected(self) -> bool:
        """
        Quick connection check to ESP32
        
        Returns:
            True if ESP32 is reachable, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/data", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def configure_esp32(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Send configuration to ESP32 (future feature)
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (success, message)
        """
        # This could be used to configure ESP32 settings in the future
        # For now, just return not implemented
        logger.info("ESP32 configuration endpoint not yet implemented")
        return False, "ESP32 configuration not yet implemented"
    
    def get_sensor_history(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get sensor reading history (future feature)
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            Dictionary with historical data
        """
        # This could be used to get historical sensor data
        # For now, just return current status
        logger.info("ESP32 history endpoint not yet implemented")
        return {
            "history_available": False,
            "message": "Historical data tracking not yet implemented",
            "current_data": self.last_data.to_dict() if self.last_data else None
        }
    
    def update_slot_status(self, slot_id: int, occupied: bool, sensor_value: int = 0, timestamp: str = "") -> Tuple[bool, str]:
        """
        Update parking slot status from ESP32 sensor data
        
        Args:
            slot_id: Slot number
            occupied: Whether slot is occupied
            sensor_value: Raw sensor value
            timestamp: Timestamp string
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"ESP32: Updating slot {slot_id} - occupied: {occupied}, value: {sensor_value}")
            
            # For now, just log the update since we don't have persistent slot storage
            # In a full implementation, this would update a database or cache
            
            if self.last_data:
                # Try to find and update the slot in cached data
                for slot in self.last_data.slots:
                    if slot.slot_id == slot_id:
                        slot.occupied = occupied
                        slot.distance_cm = sensor_value if sensor_value > 0 else slot.distance_cm
                        slot.timestamp = timestamp or slot.timestamp
                        break
            
            # Log the update
            status_text = "occupied" if occupied else "available"
            message = f"Slot {slot_id} updated to {status_text}"
            logger.info(f"ESP32: {message}")
            
            return True, message
            
        except Exception as e:
            error_msg = f"Failed to update slot {slot_id}: {str(e)}"
            logger.error(f"ESP32: {error_msg}")
            return False, error_msg
    
    def __str__(self):
        return f"ESP32Service({self.base_url})"
    
    def __repr__(self):
        connected = self.is_connected()
        return f"ESP32Service(url='{self.base_url}', connected={connected})"