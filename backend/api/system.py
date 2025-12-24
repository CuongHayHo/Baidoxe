"""
System API - General system endpoints and health checks
Xử lý các API endpoints hệ thống chung
"""
from flask import Blueprint, request, jsonify
import logging
import os
import platform
from datetime import datetime, timezone
from typing import Dict, Any

from services.card_service import CardService
from services.esp32_service import ESP32Service
from config.config import (
    CARDS_FILE, UNKNOWN_CARDS_FILE, ESP32_IP, ESP32_PORT, 
    ESP32_TIMEOUT, DETECTION_THRESHOLD, DEBUG_MODE
)

logger = logging.getLogger(__name__)

# Create blueprint for system API
system_bp = Blueprint('system', __name__, url_prefix='/api/system')

# Initialize services
card_service = CardService()
esp32_service = ESP32Service()

@system_bp.route('/health', methods=['GET'])
def health_check():
    """
    Complete system health check
    
    Returns:
        JSON response with overall system health status
    """
    try:
        logger.info("API: System health check")
        
        # Check individual components
        health_status = {
            "system": {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime": "N/A",  # Could be calculated if we track start time
                "platform": platform.system(),
                "python_version": platform.python_version()
            },
            "services": {
                "card_service": check_card_service_health(),
                "esp32_service": check_esp32_service_health()
            },
            "files": {
                "cards_file": check_file_health(CARDS_FILE),
                "unknown_cards_file": check_file_health(UNKNOWN_CARDS_FILE)
            },
            "configuration": {
                "esp32_ip": ESP32_IP,
                "esp32_port": ESP32_PORT,
                "esp32_timeout": ESP32_TIMEOUT,
                "detection_threshold": DETECTION_THRESHOLD,
                "debug_mode": DEBUG_MODE
            }
        }
        
        # Determine overall health
        overall_healthy = all([
            health_status["services"]["card_service"]["healthy"],
            health_status["services"]["esp32_service"]["healthy"],
            health_status["files"]["cards_file"]["accessible"],
            health_status["files"]["unknown_cards_file"]["accessible"]
        ])
        
        health_status["system"]["status"] = "healthy" if overall_healthy else "degraded"
        
        status_code = 200 if overall_healthy else 503
        
        return jsonify({
            "success": True,
            "healthy": overall_healthy,
            "health": health_status,
            "message": "System health check completed"
        }), status_code
        
    except Exception as e:
        logger.error(f"Error in system health check: {e}")
        return jsonify({
            "success": False,
            "healthy": False,
            "error": "Health check failed",
            "message": f"Lỗi kiểm tra hệ thống: {str(e)}"
        }), 500

@system_bp.route('/status', methods=['GET'])
def get_system_status():
    """
    Get detailed system status information
    
    Returns:
        JSON response with system status details
    """
    try:
        logger.info("API: Getting system status")
        
        # Get statistics from services
        card_stats = card_service.get_statistics()
        esp32_status = esp32_service.get_system_status()
        
        # Compile system status
        system_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "card_management": {
                    "active": True,
                    "statistics": card_stats,
                    "files": {
                        "cards_file": str(CARDS_FILE),
                        "unknown_cards_file": str(UNKNOWN_CARDS_FILE)
                    }
                },
                "esp32_communication": esp32_status
            },
            "configuration": {
                "esp32_endpoint": f"http://{ESP32_IP}:{ESP32_PORT}",
                "timeout_seconds": ESP32_TIMEOUT,
                "detection_threshold_cm": DETECTION_THRESHOLD,
                "debug_mode": DEBUG_MODE
            },
            "runtime": {
                "platform": platform.system(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
                "working_directory": os.getcwd()
            }
        }
        
        return jsonify({
            "success": True,
            "status": system_status,
            "message": "System status retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@system_bp.route('/info', methods=['GET'])
def get_system_info():
    """
    Get basic system information
    
    Returns:
        JSON response with system info
    """
    try:
        logger.info("API: Getting system info")
        
        system_info = {
            "application": {
                "name": "Parking Management System",
                "version": "1.0.0",
                "description": "Hệ thống quản lý bãi đỗ xe với RFID và cảm biến ESP32"
            },
            "api": {
                "version": "v1",
                "endpoints": {
                    "cards": "/api/cards",
                    "parking_slots": "/api/parking-slots",
                    "system": "/api/system"
                }
            },
            "hardware": {
                "esp32_sensors": {
                    "ip": ESP32_IP,
                    "port": ESP32_PORT,
                    "timeout": ESP32_TIMEOUT
                },
                "uno_r4_wifi": {
                    "function": "RFID card reader",
                    "communication": "HTTP requests to Flask server"
                }
            },
            "features": [
                "RFID card management",
                "Real-time parking slot detection", 
                "Unknown card tracking",
                "Statistics and reporting",
                "Web-based dashboard",
                "Arduino hardware integration"
            ]
        }
        
        return jsonify({
            "success": True,
            "info": system_info,
            "message": "System information retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@system_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """
    Get recent system logs (if logging to file)
    
    Query Parameters:
        lines (int): Number of lines to return (default: 100)
        level (str): Log level filter (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        JSON response with log entries
    """
    try:
        logger.info("API: Getting system logs")
        
        # Get parameters
        lines = request.args.get('lines', 100)
        level_filter = request.args.get('level', '').upper()
        
        try:
            lines = int(lines)
            lines = max(1, min(lines, 1000))  # Limit between 1-1000
        except ValueError:
            lines = 100
        
        # For now, return a placeholder response
        # In a real implementation, you would read from log files
        log_response = {
            "logs_available": False,
            "message": "Log file reading not implemented yet",
            "suggestion": "Check console output or configure file logging",
            "requested_lines": lines,
            "level_filter": level_filter if level_filter else "ALL"
        }
        
        return jsonify({
            "success": True,
            "logs": log_response,
            "message": "Log request processed"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@system_bp.route('/restart', methods=['POST'])
def restart_system():
    """
    Restart system components (placeholder for future implementation)
    
    Returns:
        JSON response with restart status
    """
    try:
        logger.info("API: System restart requested")
        
        # For now, just return a placeholder
        # In a real implementation, this might restart services or reload config
        
        return jsonify({
            "success": False,
            "error": "Not implemented",
            "message": "System restart feature not yet implemented",
            "suggestion": "Manually restart the application"
        }), 501  # Not Implemented
        
    except Exception as e:
        logger.error(f"Error in system restart: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@system_bp.route('/time', methods=['GET'])
def get_system_time():
    """
    Get current system time and timezone information
    
    Returns:
        JSON response with time information
    """
    try:
        now = datetime.now()
        utc_now = datetime.now(timezone.utc)
        
        time_info = {
            "local_time": now.isoformat(),
            "utc_time": utc_now.isoformat(),
            "timezone": str(now.astimezone().tzinfo),
            "timestamp": now.timestamp(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify({
            "success": True,
            "time": time_info,
            "message": "System time retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system time: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

# Helper functions for health checks
def check_card_service_health() -> Dict[str, Any]:
    """Check card service health"""
    try:
        cards = card_service.get_all_cards()
        return {
            "healthy": True,
            "message": "Card service operational",
            "card_count": len(cards)
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Card service error: {str(e)}",
            "card_count": 0
        }

def check_esp32_service_health() -> Dict[str, Any]:
    """Check ESP32 service health"""
    try:
        connected = esp32_service.is_connected()
        return {
            "healthy": connected,
            "message": "ESP32 connected" if connected else "ESP32 not reachable",
            "url": esp32_service.base_url
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"ESP32 service error: {str(e)}",
            "url": esp32_service.base_url
        }

def check_file_health(file_path) -> Dict[str, Any]:
    """Check file accessibility"""
    try:
        # Convert pathlib.Path to string if needed
        file_path_str = str(file_path)
        accessible = os.path.exists(file_path_str)
        size = os.path.getsize(file_path_str) if accessible else 0
        return {
            "accessible": accessible,
            "path": file_path_str,
            "size_bytes": size,
            "message": "File accessible" if accessible else "File not found"
        }
    except Exception as e:
        return {
            "accessible": False,
            "path": str(file_path),
            "size_bytes": 0,
            "message": f"File error: {str(e)}"
        }