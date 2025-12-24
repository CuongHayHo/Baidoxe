"""
Cards API - Endpoints for parking card management
Xử lý tất cả API endpoints liên quan đến thẻ xe
"""
from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
from datetime import datetime, timezone

from services.card_service import CardService
from utils.validation import ValidationHelper

logger = logging.getLogger(__name__)

# Create blueprint for cards API
cards_bp = Blueprint('cards', __name__, url_prefix='/api/cards')

# Initialize card service
card_service = CardService()

@cards_bp.route('/', methods=['GET'])
def get_all_cards():
    """
    Lấy tất cả thẻ đỗ xe trong hệ thống
    
    Returns:
        JSON response chứa danh sách thẻ hoặc lỗi
    """
    try:
        logger.info("API: Getting all cards")
        
        cards_dict = card_service.get_all_cards()
        
        # Convert ParkingCard objects to dict format for JSON response
        cards_data = [card.to_dict() for card in cards_dict.values()]
        
        return jsonify({
            "success": True,
            "cards": cards_data,
            "count": len(cards_data),
            "message": "Cards retrieved successfully"
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting all cards: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/<card_id>', methods=['GET'])
def get_card(card_id: str):
    """
    Lấy thông tin chi tiết của một thẻ cụ thể
    
    Args:
        card_id: ID của thẻ cần lấy thông tin
        
    Returns:
        JSON response chứa dữ liệu thẻ hoặc lỗi
    """
    try:
        logger.info(f"API: Getting card {card_id}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        success, card_data = card_service.get_card(clean_id)
        
        if success and card_data:
            return jsonify({
                "success": True,
                "card": card_data,
                "message": "Card found successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Card not found",
                "message": f"Không tìm thấy thẻ có ID: {clean_id}"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting card {card_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/', methods=['POST'])
def create_card():
    """
    Create new parking card
    
    Returns:
        JSON response with created card or error
    """
    try:
        logger.info("API: Creating new card")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type phải là application/json"
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "message": "Không có dữ liệu được gửi"
            }), 400
        
        # Validate card data
        is_valid, errors = ValidationHelper.validate_card_data(data)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "message": "Dữ liệu không hợp lệ",
                "errors": errors
            }), 400
        
        # Extract UID and convert status to numeric
        uid = data.get('id')
        status_map = {'active': 0, 'parked': 1, 'inactive': 0}  # Map string to int
        initial_status = status_map.get(data.get('status', 'active'), 0)
        
        # Create card using service
        success, message, new_card = card_service.create_card(uid, initial_status)
        
        if success:
            return jsonify({
                "success": True,
                "card": new_card.to_dict() if new_card else None,
                "message": message
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create card",
                "message": message
            }), 400
            
    except Exception as e:
        logger.error(f"Error creating card: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/<card_id>', methods=['PUT'])
def update_card(card_id: str):
    """
    Update existing card
    
    Args:
        card_id: Card ID to update
        
    Returns:
        JSON response with updated card or error
    """
    try:
        logger.info(f"API: Updating card {card_id}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type phải là application/json"
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "message": "Không có dữ liệu được gửi"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Ensure ID in data matches URL parameter
        data['id'] = clean_id
        
        # Validate card data
        is_valid, errors = ValidationHelper.validate_card_data(data)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "message": "Dữ liệu không hợp lệ",
                "errors": errors
            }), 400
        
        # Update card using service
        success, result = card_service.update_card(clean_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "card": result,
                "message": "Card updated successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update card",
                "message": result  # result contains error message
            }), 400
            
    except Exception as e:
        logger.error(f"Error updating card {card_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/<card_id>', methods=['DELETE'])
def delete_card(card_id: str):
    """
    Delete card
    
    Args:
        card_id: Card ID to delete
        
    Returns:
        JSON response with success status or error
    """
    try:
        logger.info(f"API: Deleting card {card_id}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Delete card using service
        success, message = card_service.delete_card(clean_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Card deleted successfully",
                "card_id": clean_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to delete card",
                "message": message
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting card {card_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/<card_id>/status', methods=['POST'])
def update_card_status(card_id: str):
    """
    Update card parking status (park/unpark)
    
    Args:
        card_id: Card ID to update status
        
    Returns:
        JSON response with updated card or error
    """
    try:
        logger.info(f"API: Updating status for card {card_id}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Get JSON data from request (optional)
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Get status from request body
        new_status = data.get('status')
        if new_status is None:
            return jsonify({
                "success": False,
                "error": "Missing status field",
                "message": "Trường 'status' là bắt buộc (0=ra bãi, 1=vào bãi)"
            }), 400
        
        if new_status not in [0, 1]:
            return jsonify({
                "success": False,
                "error": "Invalid status value",
                "message": "Status phải là 0 (ra bãi) hoặc 1 (vào bãi)"
            }), 400
        
        # Update card status using service
        success, message, result = card_service.update_card_status(clean_id, new_status)
        
        if success:
            return jsonify({
                "success": True,
                "card": result,
                "message": message
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update status",
                "message": message
            }), 400
            
    except Exception as e:
        logger.error(f"Error updating status for card {card_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/statistics', methods=['GET'])
def get_card_statistics():
    """
    Get card usage statistics
    
    Returns:
        JSON response with statistics
    """
    try:
        logger.info("API: Getting card statistics")
        
        stats = card_service.get_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats,
            "message": "Statistics retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting card statistics: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/unknown', methods=['GET'])
def get_unknown_cards():
    """
    Get list of unknown cards detected
    
    Returns:
        JSON response with unknown cards
    """
    try:
        logger.info("API: Getting unknown cards")
        
        unknown_cards = card_service.get_unknown_cards()
        
        return jsonify({
            "success": True,
            "unknown_cards": unknown_cards,
            "count": len(unknown_cards),
            "message": "Unknown cards retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting unknown cards: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/unknown', methods=['POST'])
def add_unknown_card():
    """
    Add card to unknown cards list
    
    Returns:
        JSON response with success status
    """
    try:
        logger.info("API: Adding unknown card")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type phải là application/json"
            }), 400
        
        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({
                "success": False,
                "error": "Missing card_id",
                "message": "Thiếu thông tin card_id"
            }), 400
        
        # Validate card ID format
        card_id = data['card_id']
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Add to unknown cards
        success, message = card_service.add_unknown_card(clean_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Unknown card added successfully",
                "card_id": clean_id
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to add unknown card",
                "message": message
            }), 400
            
    except Exception as e:
        logger.error(f"Error adding unknown card: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/unknown/<card_id>', methods=['DELETE'])
def remove_unknown_card(card_id: str):
    """
    Remove card from unknown cards list
    
    Args:
        card_id: Card ID to remove
        
    Returns:
        JSON response with success status
    """
    try:
        logger.info(f"API: Removing unknown card {card_id}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid card ID",
                "message": f"ID thẻ không hợp lệ: {error_msg}"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Remove from unknown cards
        success, message = card_service.remove_unknown_card(clean_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Unknown card removed successfully",
                "card_id": clean_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to remove unknown card",
                "message": message
            }), 404
            
    except Exception as e:
        logger.error(f"Error removing unknown card {card_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/logs', methods=['GET'])
def get_card_logs():
    """
    Get card activity logs
    
    Query Parameters:
        card_id (str): Filter logs by card ID
        action (str): Filter logs by action type
        limit (int): Number of logs to return (default: 50)
        offset (int): Pagination offset
        
    Returns:
        JSON response with log entries
    """
    try:
        logger.info("API: Getting card logs")
        
        # Get query parameters
        card_id = request.args.get('card_id')
        action_str = request.args.get('action')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Convert action string to LogAction enum if provided
        action_enum = None
        if action_str:
            from services.card_log_service import LogAction
            # Map action strings to enum values
            action_map = {
                'entry': LogAction.CARD_ENTRY,
                'exit': LogAction.CARD_EXIT,
                'scan': LogAction.CARD_SCAN,
                'unknown': LogAction.UNKNOWN_CARD,
                'created': LogAction.CARD_CREATED,
                'deleted': LogAction.CARD_DELETED,
                'updated': LogAction.CARD_UPDATED,
                'backup': LogAction.SYSTEM_BACKUP,
                'restore': LogAction.SYSTEM_RESTORE
            }
            action_enum = action_map.get(action_str)
        
        # Get logs from service with total count
        result = card_service.log_service.get_logs_with_count(
            card_id=card_id,
            action=action_enum,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            "success": True,
            "logs": result["logs"],
            "count": result["total_count"],  # Tổng số logs (for pagination)
            "page_count": result["filtered_count"],  # Số logs trong page hiện tại
            "has_more": result["has_more"],  # Còn pages nữa không
            "filters": {
                "card_id": card_id,
                "action": action_str,
                "limit": limit,
                "offset": offset
            },
            "message": "Logs retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": "Invalid parameters",
            "message": f"Tham số không hợp lệ: {str(e)}"
        }), 400
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error", 
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/backup', methods=['POST'])
def create_backup():
    """
    Create manual backup of cards data
    
    Returns:
        JSON response with backup status
    """
    try:
        logger.info("API: Creating manual backup")
        
        # Get reason from request body if provided
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        
        reason = data.get('reason', 'manual_api_request')
        
        # Create backup
        success, backup_path = card_service.backup_service.create_manual_backup(reason)
        
        if success:
            return jsonify({
                "success": True,
                "backup_path": backup_path,
                "reason": reason,
                "message": "Backup created successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Backup failed",
                "message": backup_path  # backup_path contains error message on failure
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/restore', methods=['POST'])
def restore_from_backup():
    """
    Restore cards data from backup file
    
    Expected JSON payload:
    {
        "backup_filename": "cards_backup_20251007_123456_manual.json"
    }
    
    Returns:
        JSON response with restore status
    """
    try:
        logger.info("API: Restoring cards from backup")
        
        # Get backup filename from request
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        
        backup_filename = data.get('backup_filename')
        if not backup_filename:
            return jsonify({
                "success": False,
                "error": "Missing backup filename",
                "message": "Vui lòng cung cấp tên file backup"
            }), 400
        
        # Restore from backup
        success, message = card_service.backup_service.restore_from_backup(backup_filename)
        
        if success:
            # Log the restore action
            try:
                from services.card_log_service import LogAction
                card_service.log_service.add_log("SYSTEM", LogAction.SYSTEM_RESTORE, {
                    "backup_filename": backup_filename,
                    "restored_at": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to log restore action: {e}")
            
            return jsonify({
                "success": True,
                "backup_filename": backup_filename,
                "message": message
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Restore failed",
                "message": message
            }), 500
            
    except Exception as e:
        logger.error(f"Error restoring from backup: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/backups', methods=['GET'])
def list_backups():
    """
    List all available backup files
    
    Returns:
        JSON response with list of backup files
    """
    try:
        logger.info("API: Getting backup files list")
        
        # Get backup files list
        backups = card_service.backup_service.list_backups()
        
        return jsonify({
            "success": True,
            "backups": backups,
            "count": len(backups),
            "message": "Backup files retrieved successfully"
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting backup files: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Lỗi server: {str(e)}"
        }), 500

@cards_bp.route('/scan', methods=['POST'])
def scan_card():
    """
    ESP32 card scan endpoint - Process card scan from hardware
    
    Expected JSON payload:
    {
        "card_id": "A1B2C3D4",
        "timestamp": "2025-10-06T21:47:00Z"
    }
    
    Returns:
        JSON response with card status and action taken
    """
    try:
        logger.info("ESP32: Card scan received")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Invalid content type",
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({
                "success": False,
                "error": "Missing card_id",
                "message": "card_id field is required"
            }), 400
        
        card_id = str(data['card_id']).strip()
        direction = data.get('direction', '').strip().upper()  # IN hoặc OUT
        timestamp = data.get('timestamp', '')
        
        logger.info(f"UNO R4: Processing card scan - ID: {card_id}, Direction: {direction}")
        
        # Validate card ID format
        is_valid, error_msg = ValidationHelper.validate_card_id(card_id)
        if not is_valid:
            logger.warning(f"ESP32: Invalid card format - {card_id}: {error_msg}")
            return jsonify({
                "success": False,
                "error": "Invalid card ID format",
                "message": f"Invalid card ID: {error_msg}",
                "action": "reject"
            }), 400
        
        # Clean card ID
        clean_id = ValidationHelper.clean_card_id(card_id)
        
        # Check if card exists in system
        success, card_data = card_service.get_card(clean_id)
        
        if success and card_data:
            # Known card - determine action based on direction and current status
            current_status = card_data.get('status', 0)
            
            # Logic: IN reader = entry (status 0->1), OUT reader = exit (status 1->0)
            if direction == 'IN':
                # IN reader: Xe vào bãi (nếu đang ngoài)
                if current_status == 0:
                    new_status = 1  # Vào bãi
                    action = "entry"
                else:
                    # Đã ở trong bãi rồi, từ chối
                    return jsonify({
                        "success": False,
                        "error": "Invalid entry",
                        "message": f"Xe đã ở trong bãi rồi",
                        "action": "reject",
                        "current_status": "parked"
                    }), 400
            
            elif direction == 'OUT':
                # OUT reader: Xe ra khỏi bãi (nếu đang trong)
                if current_status == 1:
                    new_status = 0  # Ra khỏi bãi
                    action = "exit"
                else:
                    # Đang ở ngoài bãi rồi, từ chối
                    return jsonify({
                        "success": False,
                        "error": "Invalid exit",
                        "message": f"Xe đang ở ngoài bãi rồi",
                        "action": "reject",
                        "current_status": "available"
                    }), 400
            
            else:
                # Direction không rõ, fallback về toggle cũ
                new_status = 1 - current_status
                action = "entry" if new_status == 1 else "exit"
            
            # Update card status
            update_success, message, updated_card = card_service.update_card_status(clean_id, new_status)
            
            if update_success:
                # action đã được xác định ở trên dựa trên direction
                
                # ✅ FIX: Chỉ log entry/exit, không log scan riêng để tránh lặp nhật ký
                # Log entry hoặc exit (không log scan riêng)
                if new_status == 1:
                    card_service.log_service.log_card_entry(clean_id, {
                        "timestamp": timestamp,
                        "direction": direction,
                        "source": "uno_r4_wifi"
                    })
                else:
                    card_service.log_service.log_card_exit(clean_id, {
                        "timestamp": timestamp,
                        "direction": direction,
                        "source": "uno_r4_wifi"
                    })
                
                logger.info(f"UNO R4: Card {clean_id} - {action} processed successfully (Direction: {direction})")
                
                return jsonify({
                    "success": True,
                    "card": updated_card,
                    "action": action,
                    "direction": direction,
                    "message": f"Card {action} processed",
                    "parking_status": "parked" if new_status == 1 else "available",
                    "timestamp": timestamp
                }), 200
            else:
                logger.error(f"UNO R4: Failed to update card {clean_id}: {message}")
                return jsonify({
                    "success": False,
                    "error": "Status update failed",
                    "message": message,
                    "action": "error"
                }), 500
                
        else:
            # Unknown card - add to unknown list and reject
            logger.warning(f"UNO R4: Unknown card detected - {clean_id} (Direction: {direction})")
            
            # Log unknown card detection
            card_service.log_service.log_unknown_card(clean_id, "uno_r4")
            
            # Add to unknown cards list
            add_success, add_message = card_service.add_unknown_card(clean_id)
            
            return jsonify({
                "success": False,
                "error": "Unknown card",
                "message": f"Card not registered in system: {clean_id}",
                "action": "reject",
                "card_id": clean_id,
                "unknown_card_logged": add_success,
                "timestamp": timestamp
            }), 403
            
    except Exception as e:
        logger.error(f"UNO R4: Error processing card scan: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": f"Server error: {str(e)}",
            "action": "error"
        }), 500


@cards_bp.route('/fix-data', methods=['POST'])
def fix_card_data():
    """
    Fix corrupted card data with negative parking durations
    Admin endpoint to clean up invalid time data
    """
    try:
        logger.info("Starting card data cleanup for negative durations")
        
        # Get all cards
        cards = card_service.get_all_cards()
        
        fixed_count = 0
        error_cards = []
        
        for uid, card in cards.items():
            try:
                # Force recalculate parking duration which will fix negative values
                card._calculate_parking_duration()
                
                # Check if card had negative duration (now fixed)
                if card.parking_duration and card.parking_duration.get("display", "").startswith("Dữ liệu lỗi"):
                    fixed_count += 1
                    error_cards.append({
                        "uid": uid,
                        "issue": "Negative parking duration fixed",
                        "exit_time_cleared": card.exit_time is None
                    })
                    
            except Exception as e:
                logger.warning(f"Error fixing card {uid}: {e}")
                error_cards.append({
                    "uid": uid,
                    "issue": f"Error during fix: {e}"
                })
        
        # Save the fixed data
        cards_data = {}
        for card_uid, card_obj in cards.items():
            cards_data[card_uid] = card_obj.to_dict()
        
        from config.config import CARDS_FILE
        success, message = card_service.file_manager.write_json(CARDS_FILE, cards_data)
        
        if success:
            # Create backup after data fix
            card_service._auto_backup_if_needed("data_cleanup_negative_durations")
            
            return jsonify({
                "success": True,
                "message": f"Card data cleanup completed successfully",
                "fixed_count": fixed_count,
                "total_cards": len(cards),
                "error_details": error_cards if error_cards else None,
                "backup_created": True
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save fixed data",
                "message": message
            }), 500
            
    except Exception as e:
        logger.error(f"Error in card data cleanup: {e}")
        return jsonify({
            "success": False,
            "error": "Data cleanup failed",
            "message": str(e)
        }), 500