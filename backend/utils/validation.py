"""
Validation Helper - Bộ công cụ validation dữ liệu đầu vào

Chức năng chính:
- Validation format cho RFID card IDs
- Validation cấu trúc dữ liệu thẻ và sensor
- Kiểm tra timestamp, IP address, port number
- Sanitization và normalization dữ liệu đầu vào
- Validation cấu hình hệ thống
- Security checks cho filename và input data
"""
import re
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ValidationHelper:
    """
    Lớp utility chứa các phương thức validation dữ liệu
    
    Provides static methods để validate:
    - RFID card IDs và card data
    - ESP32 sensor data
    - Network configuration (IP, port)
    - Timestamps và JSON structure
    - Application configuration
    """
    
    # Regex patterns cho validation
    CARD_ID_PATTERN = re.compile(r'^[A-Za-z0-9]{4,16}$')  # Chuỗi alphanumeric 4-16 ký tự
    IP_ADDRESS_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    @staticmethod
    def validate_card_id(card_id: Any) -> Tuple[bool, str]:
        """
        Kiểm tra format của RFID card ID
        
        Args:
            card_id: ID thẻ cần kiểm tra
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not isinstance(card_id, str):
            return False, "ID thẻ phải là chuỗi"
        
        if not card_id.strip():
            return False, "ID thẻ không được để trống"
        
        # Loại bỏ khoảng trắng và chuyển thành chữ hoa để validation
        clean_id = card_id.replace(" ", "").upper()
        
        if not ValidationHelper.CARD_ID_PATTERN.match(clean_id):
            return False, "ID thẻ phải là 4-16 ký tự alphanumeric"
        
        return True, ""
    
    @staticmethod
    def validate_card_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate parking card data structure
        
        Args:
            data: Card data dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'status']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not data[field]:
                errors.append(f"Field '{field}' cannot be empty")
        
        # Validate card ID format
        if 'id' in data:
            is_valid, error_msg = ValidationHelper.validate_card_id(data['id'])
            if not is_valid:
                errors.append(f"Invalid card ID: {error_msg}")
        
        # Validate name
        if 'name' in data:
            if not isinstance(data['name'], str):
                errors.append("Card name must be a string")
            elif len(data['name'].strip()) < 2:
                errors.append("Card name must be at least 2 characters")
            elif len(data['name'].strip()) > 100:
                errors.append("Card name cannot exceed 100 characters")
        
        # Validate status
        valid_statuses = ['active', 'parked', 'inactive', 'outside', 'inside']
        if 'status' in data:
            if data['status'] not in valid_statuses:
                errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Validate optional fields
        if 'parked_at' in data and data['parked_at'] is not None:
            if not ValidationHelper.validate_timestamp(data['parked_at']):
                errors.append("Invalid parked_at timestamp format")
        
        if 'created_at' in data and data['created_at'] is not None:
            if not ValidationHelper.validate_timestamp(data['created_at']):
                errors.append("Invalid created_at timestamp format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_parking_slot_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate parking slot sensor data
        
        Args:
            data: Parking slot data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level fields
        if 'esp32_data' not in data:
            errors.append("Missing esp32_data field")
            return False, errors
        
        esp32_data = data['esp32_data']
        
        # Validate ESP32 data structure
        required_esp32_fields = ['soIC', 'totalSensors', 'data']
        for field in required_esp32_fields:
            if field not in esp32_data:
                errors.append(f"Missing ESP32 field: {field}")
        
        # Validate soIC (number of ICs)
        if 'soIC' in esp32_data:
            if not isinstance(esp32_data['soIC'], int) or esp32_data['soIC'] < 1:
                errors.append("soIC must be a positive integer")
        
        # Validate totalSensors
        if 'totalSensors' in esp32_data:
            if not isinstance(esp32_data['totalSensors'], int) or esp32_data['totalSensors'] < 1:
                errors.append("totalSensors must be a positive integer")
        
        # Validate sensor data array
        if 'data' in esp32_data:
            sensor_data = esp32_data['data']
            if not isinstance(sensor_data, list):
                errors.append("ESP32 data field must be a list")
            else:
                for i, distance in enumerate(sensor_data):
                    if not isinstance(distance, (int, float)):
                        errors.append(f"Sensor {i} distance must be a number")
                    elif distance < 0:
                        errors.append(f"Sensor {i} distance cannot be negative")
                    elif distance > 1000:  # Max reasonable distance in cm
                        errors.append(f"Sensor {i} distance {distance}cm seems unreasonable")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_timestamp(timestamp: Any) -> bool:
        """
        Validate timestamp format (ISO 8601)
        
        Args:
            timestamp: Timestamp to validate
            
        Returns:
            True if valid timestamp, False otherwise
        """
        if not isinstance(timestamp, str):
            return False
        
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ip_address(ip: Any) -> Tuple[bool, str]:
        """
        Validate IP address format
        
        Args:
            ip: IP address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(ip, str):
            return False, "IP address must be a string"
        
        if not ValidationHelper.IP_ADDRESS_PATTERN.match(ip.strip()):
            return False, "Invalid IP address format"
        
        return True, ""
    
    @staticmethod
    def validate_port(port: Any) -> Tuple[bool, str]:
        """
        Validate network port number
        
        Args:
            port: Port number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(port, int):
            return False, "Port must be an integer"
        
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
        
        return True, ""
    
    @staticmethod
    def sanitize_string(value: Any, max_length: int = 255) -> str:
        """
        Sanitize string input by removing dangerous characters and limiting length
        
        Args:
            value: Value to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes and control characters except tab, newline, carriage return
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def validate_json_structure(data: Any, required_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that JSON data has required structure
        
        Args:
            data: Data to validate
            required_keys: List of required keys
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary/object")
            return False, errors
        
        for key in required_keys:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: Optional[float] = None, 
                             max_val: Optional[float] = None, field_name: str = "Value") -> Tuple[bool, str]:
        """
        Validate numeric value is within specified range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Name of field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{field_name} must be a number"
        
        if min_val is not None and value < min_val:
            return False, f"{field_name} must be at least {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"{field_name} must not exceed {max_val}"
        
        return True, ""
    
    @staticmethod
    def clean_card_id(card_id: str) -> str:
        """
        Clean and normalize card ID format
        
        Args:
            card_id: Raw card ID
            
        Returns:
            Cleaned card ID in uppercase without spaces
        """
        if not isinstance(card_id, str):
            return str(card_id)
        
        # Remove spaces and convert to uppercase
        return card_id.replace(" ", "").upper().strip()
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate application configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required config fields
        required_fields = ['ESP32_IP', 'ESP32_PORT', 'CARDS_FILE', 'UNKNOWN_CARDS_FILE']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing configuration field: {field}")
        
        # Validate ESP32 IP
        if 'ESP32_IP' in config:
            is_valid, error_msg = ValidationHelper.validate_ip_address(config['ESP32_IP'])
            if not is_valid:
                errors.append(f"Invalid ESP32_IP: {error_msg}")
        
        # Validate ESP32 port
        if 'ESP32_PORT' in config:
            is_valid, error_msg = ValidationHelper.validate_port(config['ESP32_PORT'])
            if not is_valid:
                errors.append(f"Invalid ESP32_PORT: {error_msg}")
        
        # Validate file paths
        for file_field in ['CARDS_FILE', 'UNKNOWN_CARDS_FILE']:
            if file_field in config:
                if not isinstance(config[file_field], str) or not config[file_field].strip():
                    errors.append(f"{file_field} must be a non-empty string")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """
        Check if filename is safe (no path traversal, dangerous chars)
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename is safe, False otherwise
        """
        if not isinstance(filename, str) or not filename.strip():
            return False
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for dangerous characters
        dangerous_chars = '<>:"|?*'
        if any(char in filename for char in dangerous_chars):
            return False
        
        return True


# ============ User Validation Functions ============

def validate_username(username: str) -> bool:
    """
    Validate username format
    Requirements: 3-20 characters, alphanumeric + underscore only
    """
    if not isinstance(username, str):
        return False
    
    if len(username) < 3 or len(username) > 20:
        return False
    
    # Allow alphanumeric and underscore only
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def validate_password(password: str) -> bool:
    """
    Validate password strength
    Requirements: at least 6 characters
    """
    if not isinstance(password, str):
        return False
    
    return len(password) >= 6