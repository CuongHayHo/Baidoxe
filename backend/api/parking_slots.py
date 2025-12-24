"""
Parking Slots API - Endpoints for ESP32 sensor data
Xử lý tất cả API endpoints liên quan đến cảm biến bãi đỗ xe
"""
from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any

from services.esp32_service import ESP32Service
from utils.validation import ValidationHelper

logger = logging.getLogger(__name__)

# Create blueprint for parking slots API
parking_slots_bp = Blueprint('parking_slots', __name__, url_prefix='/api/parking-slots')

# Initialize ESP32 service
esp32_service = ESP32Service()

@parking_slots_bp.route('/', methods=['GET'])
def get_parking_slots():
    """
    Get current parking slots data from ESP32
    
    Query Parameters:
        reset (bool): Whether to reset sensors before reading
        
    Returns:
        JSON response with parking slots data or error
    """
    try:
        logger.info("API: Getting parking slots data")
        
        # Check for reset parameter
        reset_requested = request.args.get('reset', '').lower() in ['true', '1', 'yes']
        
        # Get data from ESP32
        success, raw_data, slots_data = esp32_service.get_parking_slots(force_reset=reset_requested)
        
        if success and slots_data:
            response_data = {
                "success": True,
                "data": slots_data.to_dict(),
                "summary": slots_data.summary,
                "validation": slots_data.validate(),
                "reset_performed": raw_data.get("reset_performed", False),
                "message": "Parking slots data retrieved successfully"
            }
            return jsonify(response_data), 200
        else:
            # Return error response from ESP32Service
            error_response = {
                "success": False,
                "data": None,
                "error": raw_data.get("error", "Unknown error"),
                "message": raw_data.get("message", "Failed to get parking slots data"),
                "esp32_url": esp32_service.base_url
            }
            
            # Determine appropriate HTTP status code
            status_code = 503  # Service Unavailable (ESP32 connection issues)
            if "timeout" in raw_data.get("error", "").lower():
                status_code = 504  # Gateway Timeout
            elif "HTTP error" in raw_data.get("error", ""):
                status_code = 502  # Bad Gateway
            
            return jsonify(error_response), status_code
            
    except Exception as e:
        logger.error(f"Error getting parking slots: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/reset', methods=['POST'])
def reset_sensors():
    """
    Reset ESP32 sensors
    
    Returns:
        JSON response with reset status
    """
    try:
        logger.info("API: Resetting ESP32 sensors")
        
        # Reset sensors using service
        success, message = esp32_service.reset_sensors()
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "action": "sensors_reset"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Reset failed",
                "message": message,
                "esp32_url": esp32_service.base_url
            }), 503  # Service Unavailable
            
    except Exception as e:
        logger.error(f"Error resetting sensors: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/status', methods=['GET'])
def get_system_status():
    """
    Get ESP32 system status and health check
    
    Returns:
        JSON response with system status
    """
    try:
        logger.info("API: Getting system status")
        
        # Get system status from service
        status = esp32_service.get_system_status()
        
        return jsonify({
            "success": True,
            "system_status": status,
            "message": "System status retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/cached', methods=['GET'])
def get_cached_data():
    """
    Get last cached parking slots data (without ESP32 request)
    
    Returns:
        JSON response with cached data or empty response
    """
    try:
        logger.info("API: Getting cached parking slots data")
        
        # Get cached data from service
        cached_data = esp32_service.get_cached_data()
        
        if cached_data:
            return jsonify({
                "success": True,
                "data": cached_data.to_dict(),
                "summary": cached_data.summary,
                "validation": cached_data.validate(),
                "cached": True,
                "last_updated": esp32_service.last_updated,
                "message": "Cached data retrieved successfully"
            }), 200
        else:
            return jsonify({
                "success": True,
                "data": None,
                "cached": False,
                "message": "No cached data available"
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting cached data: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/health', methods=['GET'])
def health_check():
    """
    Quick health check for ESP32 connectivity
    
    Returns:
        JSON response with health status
    """
    try:
        logger.info("API: ESP32 health check")
        
        # Quick connection check
        is_connected = esp32_service.is_connected()
        
        response_data = {
            "success": True,
            "esp32_connected": is_connected,
            "esp32_url": esp32_service.base_url,
            "timeout_setting": esp32_service.timeout,
            "message": "ESP32 connected" if is_connected else "ESP32 not reachable"
        }
        
        status_code = 200 if is_connected else 503
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            "success": False,
            "esp32_connected": False,
            "error": "Health check failed",
            "message": f"Lỗi kiểm tra kết nối: {str(e)}"
        }), 500

@parking_slots_bp.route('/history', methods=['GET'])
def get_sensor_history():
    """
    Get sensor reading history (future feature)
    
    Query Parameters:
        hours (int): Number of hours of history (default: 24)
        
    Returns:
        JSON response with historical data
    """
    try:
        logger.info("API: Getting sensor history")
        
        # Get hours parameter
        hours = request.args.get('hours', 24)
        try:
            hours = int(hours)
            if hours < 1 or hours > 168:  # Limit to 1 week
                hours = 24
        except ValueError:
            hours = 24
        
        # Get history from service
        history_data = esp32_service.get_sensor_history(hours)
        
        return jsonify({
            "success": True,
            "history": history_data,
            "hours_requested": hours,
            "message": "Sensor history retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sensor history: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/configure', methods=['POST'])
def configure_esp32():
    """
    Configure ESP32 settings (future feature)
    
    Returns:
        JSON response with configuration status
    """
    try:
        logger.info("API: Configuring ESP32")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type phải là application/json"
            }), 400
        
        config_data = request.get_json()
        if not config_data:
            return jsonify({
                "success": False,
                "error": "No configuration data provided",
                "message": "Không có dữ liệu cấu hình"
            }), 400
        
        # Validate configuration (basic validation)
        if not isinstance(config_data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid configuration format",
                "message": "Định dạng cấu hình không hợp lệ"
            }), 400
        
        # Send configuration to ESP32
        success, message = esp32_service.configure_esp32(config_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "configuration": config_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Configuration failed",
                "message": message
            }), 501  # Not Implemented
            
    except Exception as e:
        logger.error(f"Error configuring ESP32: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/slots/<int:slot_id>', methods=['GET'])
def get_single_slot(slot_id: int):
    """
    Get data for a specific parking slot
    
    Args:
        slot_id: Slot number (0-based index)
        
    Returns:
        JSON response with single slot data
    """
    try:
        logger.info(f"API: Getting slot {slot_id} data")
        
        # Validate slot ID
        if slot_id < 0 or slot_id > 10:  # Reasonable limit
            return jsonify({
                "success": False,
                "error": "Invalid slot ID",
                "message": f"Slot ID phải từ 0-10, nhận được: {slot_id}"
            }), 400
        
        # Get current data
        success, raw_data, slots_data = esp32_service.get_parking_slots(force_reset=False)
        
        if success and slots_data:
            # Find the specific slot
            target_slot = None
            for slot in slots_data.slots:
                if slot.slot_id == slot_id:
                    target_slot = slot
                    break
            
            if target_slot:
                return jsonify({
                    "success": True,
                    "slot": target_slot.to_dict(),
                    "message": f"Slot {slot_id} data retrieved successfully"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Slot not found",
                    "message": f"Không tìm thấy slot {slot_id}"
                }), 404
        else:
            return jsonify({
                "success": False,
                "error": "Failed to get slots data",
                "message": raw_data.get("message", "Không thể lấy dữ liệu slots")
            }), 503
            
    except Exception as e:
        logger.error(f"Error getting slot {slot_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@parking_slots_bp.route('/update', methods=['POST'])
def update_parking_slot():
    """
    ESP32 sensor update endpoint - Receive sensor data from hardware
    
    Expected JSON payload:
    {
        "slot_id": 1,
        "occupied": true,
        "timestamp": "2025-10-06T21:47:00Z",
        "sensor_value": 123 (optional)
    }
    
    Returns:
        JSON response with update confirmation
    """
    try:
        logger.info("ESP32: Parking slot update received")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "message": "No sensor data received"
            }), 400
        
        # Validate required fields
        required_fields = ['slot_id', 'occupied']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": "Missing required fields",
                "message": f"Required fields: {missing_fields}",
                "required": required_fields
            }), 400
        
        slot_id = data.get('slot_id')
        occupied = data.get('occupied')
        timestamp = data.get('timestamp', '')
        sensor_value = data.get('sensor_value', 0)
        
        # Validate slot_id
        if not isinstance(slot_id, int) or slot_id < 0 or slot_id > 10:
            return jsonify({
                "success": False,
                "error": "Invalid slot_id",
                "message": f"slot_id must be integer 0-10, got: {slot_id}"
            }), 400
        
        # Validate occupied status
        if not isinstance(occupied, bool):
            return jsonify({
                "success": False,
                "error": "Invalid occupied value",
                "message": f"occupied must be boolean, got: {type(occupied).__name__}"
            }), 400
        
        logger.info(f"ESP32: Slot {slot_id} update - occupied: {occupied}, value: {sensor_value}")
        
        # Process sensor update via service
        success, message = esp32_service.update_slot_status(slot_id, occupied, sensor_value, timestamp)
        
        if success:
            logger.info(f"ESP32: Slot {slot_id} updated successfully")
            return jsonify({
                "success": True,
                "slot_id": slot_id,
                "occupied": occupied,
                "sensor_value": sensor_value,
                "message": message,
                "timestamp": timestamp,
                "action": "sensor_update"
            }), 200
        else:
            logger.error(f"ESP32: Failed to update slot {slot_id}: {message}")
            return jsonify({
                "success": False,
                "error": "Update failed",
                "message": message,
                "slot_id": slot_id,
                "action": "error"
            }), 500
            
    except Exception as e:
        logger.error(f"ESP32: Error processing slot update: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Server error: {str(e)}",
            "action": "error"
        }), 500