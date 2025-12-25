"""
Card Log Service - Logging tất cả hoạt động của thẻ đỗ xe
Ghi log chi tiết cho mọi thao tác: vào/ra bãi, thêm/xóa thẻ, etc.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

from config.config import CARDS_FILE

logger = logging.getLogger(__name__)

class LogAction(Enum):
    """Enum định nghĩa các loại hành động log"""
    CARD_ENTRY = "entry"           # Thẻ vào bãi
    CARD_EXIT = "exit"             # Thẻ ra bãi  
    CARD_SCAN = "scan"             # ESP32/Arduino scan thẻ
    CARD_CREATED = "created"       # Thêm thẻ mới vào hệ thống
    CARD_DELETED = "deleted"       # Xóa thẻ khỏi hệ thống
    CARD_UPDATED = "updated"       # Cập nhật thông tin thẻ
    UNKNOWN_CARD = "unknown"       # Phát hiện thẻ lạ
    SYSTEM_BACKUP = "backup"       # Tạo backup
    SYSTEM_RESTORE = "restore"     # Khôi phục từ backup

class CardLogService:
    """
    Service class for logging all card-related activities
    """
    
    def __init__(self):
        """Initialize card log service"""
        # File lưu logs
        self.log_file = Path(CARDS_FILE).parent / "card_logs.json"
        
        # Đảm bảo file log tồn tại
        self._ensure_log_file()
        
        # Migrate existing logs to use UUID if needed
        self._migrate_old_log_ids()
        
        logger.info(f"CardLogService initialized - log file: {self.log_file}")
    
    def _ensure_log_file(self):
        """Tạo file log nếu chưa tồn tại"""
        try:
            if not self.log_file.exists():
                # Tạo file log với cấu trúc mặc định
                initial_data = {
                    "logs": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0"
                }
                
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                
                logger.info("Created new card log file")
                
        except Exception as e:
            logger.error(f"Failed to create log file: {e}")
    
    def _migrate_old_log_ids(self):
        """Migrate old timestamp-based IDs to UUID-based IDs to fix duplicates"""
        try:
            log_data = self._read_log_file()
            logs = log_data.get("logs", [])
            
            # Check if migration is needed (old IDs start with "log_")
            if logs and logs[0].get("id", "").startswith("log_"):
                logger.info(f"Starting migration of {len(logs)} logs to UUID-based IDs...")
                
                # Regenerate all IDs with UUID
                for log in logs:
                    log["id"] = str(uuid.uuid4())
                
                # Write back to file
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Successfully migrated {len(logs)} logs to UUID-based IDs")
        
        except Exception as e:
            logger.warning(f"Log ID migration failed (non-critical): {e}")
    
    def add_log(self, 
                card_id: str, 
                action: LogAction, 
                details: Dict[str, Any] = None,
                metadata: Dict[str, Any] = None) -> bool:
        """
        Thêm log entry mới vào cả JSON file và database
        
        Args:
            card_id: ID của thẻ
            action: Loại hành động (LogAction enum)
            details: Chi tiết bổ sung về hành động
            metadata: Metadata khác (IP, user-agent, etc.)
            
        Returns:
            True if log added successfully
        """
        try:
            # Tạo log entry
            log_entry = {
                "id": self._generate_log_id(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "card_id": str(card_id),
                "action": action.value,
                "details": details or {},
                "metadata": metadata or {}
            }
            
            # Thêm thông tin context tự động
            log_entry["details"]["local_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # ✅ Ghi vào JSON file
            log_data = self._read_log_file()
            log_data["logs"].append(log_entry)
            
            # Giới hạn số lượng logs (tối đa 10000 entries để tránh file quá lớn)
            max_logs = 10000
            if len(log_data["logs"]) > max_logs:
                # Giữ lại 8000 logs mới nhất
                log_data["logs"] = log_data["logs"][-8000:]
                logger.info(f"Trimmed logs to keep latest 8000 entries")
            
            # Ghi lại file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            # ✅ Ghi vào database (nếu available)
            self._save_to_database(card_id, action, log_entry)
            
            logger.debug(f"Added log: {card_id} - {action.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add log entry: {e}")
            return False
    
    def _save_to_database(self, card_id: str, action: LogAction, log_entry: Dict[str, Any]):
        """
        Ghi log vào database SQLAlchemy (nếu available)
        
        Args:
            card_id: ID của thẻ
            action: LogAction enum
            log_entry: Log entry dict
        """
        try:
            # Tạo CardLogModel entry - mapping fields từ JSON sang database
            card_log_data = {
                "card_number": card_id,  # Map từ card_id
                "action": action.value,  # entry, exit, scan, unknown, created, deleted, etc
                "notes": log_entry["details"].get("local_time", ""),  # Store local_time as notes
            }
            
            # Parse timestamp safely
            try:
                timestamp_str = log_entry["timestamp"]
                if isinstance(timestamp_str, str):
                    card_log_data["timestamp"] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    card_log_data["timestamp"] = timestamp_str
            except (ValueError, KeyError):
                card_log_data["timestamp"] = datetime.now(timezone.utc)
            
            # Nếu có source info, thêm vào notes
            if "source" in log_entry["details"]:
                card_log_data["notes"] = f"{card_log_data['notes']} [Source: {log_entry['details']['source']}]"
            
            # Nếu có thêm info, thêm vào metadata
            if log_entry.get("metadata"):
                card_log_data["notes"] = f"{card_log_data['notes']} {json.dumps(log_entry['metadata'])}"
            
            # Thử import và save vào database
            try:
                from app import db as app_db
                from scripts.init_db import create_sqlalchemy_models
                
                # Get CardLogModel
                UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
                
                # Tạo record mới
                new_log = CardLogModel(**card_log_data)
                app_db.session.add(new_log)
                app_db.session.commit()
                
                logger.debug(f"Saved log to database: {card_id} - {action.value}")
            except (ImportError, AttributeError, ModuleNotFoundError):
                # CardLogModel không tồn tại hoặc SQLAlchemy chưa init
                logger.debug(f"Database not available for logging, using JSON only")
            except Exception as db_error:
                # Database error
                logger.debug(f"Database write failed: {db_error}")
                try:
                    app_db.session.rollback()
                except:
                    pass
                
        except Exception as e:
            # Không throw error - JSON log đã được lưu
            logger.debug(f"Database logging failed (non-critical): {e}")
    
    def _read_log_file(self) -> Dict[str, Any]:
        """Đọc file log, trả về dict hoặc tạo mới nếu bị lỗi"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Log file read error, creating new: {e}")
            return {
                "logs": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0"
            }
    
    def _generate_log_id(self) -> str:
        """Tạo unique ID cho log entry sử dụng UUID"""
        return str(uuid.uuid4())
    
    def get_logs_with_count(self, 
                 card_id: Optional[str] = None,
                 action: Optional[LogAction] = None,
                 limit: int = 100,
                 offset: int = 0) -> Dict[str, Any]:
        """
        Lấy danh sách logs với filter + total count cho pagination
        
        Args:
            card_id: Filter theo card ID (optional)
            action: Filter theo loại action (optional)  
            limit: Số lượng logs tối đa trả về
            offset: Bỏ qua n logs đầu tiên
            
        Returns:
            Dict với keys: logs, total_count, filtered_count
        """
        try:
            log_data = self._read_log_file()
            all_logs = log_data.get("logs", [])
            
            # Filter theo card_id nếu được chỉ định
            if card_id:
                filtered_logs = [log for log in all_logs if log.get("card_id") == card_id]
            else:
                filtered_logs = all_logs.copy()
            
            # Filter theo action nếu được chỉ định  
            if action:
                filtered_logs = [log for log in filtered_logs if log.get("action") == action.value]
            
            # Sort theo timestamp (mới nhất trước)
            filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Get total count sau khi filter
            total_count = len(filtered_logs)
            
            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_logs = filtered_logs[start_idx:end_idx]
            
            return {
                "logs": paginated_logs,
                "total_count": total_count,  # Tổng số logs sau filter
                "filtered_count": len(paginated_logs),  # Số logs trong page hiện tại
                "has_more": end_idx < total_count  # Còn pages nữa không
            }
            
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return {
                "logs": [],
                "total_count": 0,
                "filtered_count": 0,
                "has_more": False
            }

    def get_logs(self, 
                 card_id: Optional[str] = None,
                 action: Optional[LogAction] = None,
                 limit: int = 100,
                 offset: int = 0) -> List[Dict[str, Any]]:
        """
        Backwards compatibility method - chỉ trả về logs
        """
        result = self.get_logs_with_count(card_id, action, limit, offset)
        return result["logs"]
    
    def get_card_history(self, card_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử hoạt động của một thẻ cụ thể
        
        Args:
            card_id: ID của thẻ
            limit: Số lượng logs tối đa
            
        Returns:
            List of log entries for the card
        """
        return self.get_logs(card_id=card_id, limit=limit)
    
    def get_recent_activities(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy hoạt động gần đây trong N giờ
        
        Args:
            hours: Số giờ gần đây
            limit: Số lượng logs tối đa
            
        Returns:
            List of recent log entries
        """
        try:
            # Tính thời gian cutoff
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            logs = self.get_logs(limit=limit * 2)  # Lấy nhiều hơn để filter
            
            # Filter theo thời gian
            recent_logs = []
            for log in logs:
                try:
                    log_time = datetime.fromisoformat(log["timestamp"]).timestamp()
                    if log_time >= cutoff_time:
                        recent_logs.append(log)
                except (ValueError, KeyError):
                    continue
            
            return recent_logs[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê về logs
        
        Returns:
            Dictionary with log statistics
        """
        try:
            log_data = self._read_log_file()
            logs = log_data.get("logs", [])
            
            # Đếm theo action type
            action_counts = {}
            for log in logs:
                action = log.get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1
            
            # Đếm theo ngày (7 ngày gần nhất)
            daily_counts = {}
            cutoff_time = datetime.now(timezone.utc).timestamp() - (7 * 24 * 3600)
            
            for log in logs:
                try:
                    log_time = datetime.fromisoformat(log["timestamp"])
                    if log_time.timestamp() >= cutoff_time:
                        day_key = log_time.strftime("%Y-%m-%d")
                        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
                except (ValueError, KeyError):
                    continue
            
            # Top 10 thẻ hoạt động nhiều nhất
            card_counts = {}
            for log in logs:
                card_id = log.get("card_id", "unknown")
                card_counts[card_id] = card_counts.get(card_id, 0) + 1
            
            top_cards = sorted(card_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            stats = {
                "total_logs": len(logs),
                "action_counts": action_counts,
                "daily_activity": daily_counts,
                "top_active_cards": top_cards,
                "log_file_size": self.log_file.stat().st_size if self.log_file.exists() else 0,
                "oldest_log": logs[-1]["timestamp"] if logs else None,
                "newest_log": logs[0]["timestamp"] if logs else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get log statistics: {e}")
            return {}
    
    # Convenience methods cho các actions phổ biến
    
    def log_card_entry(self, card_id: str, details: Dict = None):
        """Log khi thẻ vào bãi"""
        return self.add_log(card_id, LogAction.CARD_ENTRY, details)
    
    def log_card_exit(self, card_id: str, details: Dict = None):
        """Log khi thẻ ra bãi"""  
        return self.add_log(card_id, LogAction.CARD_EXIT, details)
    
    def log_card_scan(self, card_id: str, source: str = "esp32", details: Dict = None):
        """Log khi ESP32/Arduino scan thẻ"""
        scan_details = {"source": source}
        if details:
            scan_details.update(details)
        return self.add_log(card_id, LogAction.CARD_SCAN, scan_details)
    
    def log_card_created(self, card_id: str, initial_status: int = 0):
        """Log khi tạo thẻ mới"""
        details = {"initial_status": initial_status}
        return self.add_log(card_id, LogAction.CARD_CREATED, details)
    
    def log_card_deleted(self, card_id: str, reason: str = "manual"):
        """Log khi xóa thẻ"""
        details = {"reason": reason}
        return self.add_log(card_id, LogAction.CARD_DELETED, details)
    
    def log_unknown_card(self, card_id: str, source: str = "esp32"):
        """Log khi phát hiện thẻ lạ"""
        details = {"source": source}
        return self.add_log(card_id, LogAction.UNKNOWN_CARD, details)