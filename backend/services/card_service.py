"""
Card Service - Lớp xử lý logic nghiệp vụ cho các thao tác với thẻ đỗ xe

Chức năng chính:
- CRUD operations cho parking cards
- Quản lý unknown cards (thẻ lạ)  
- Tính toán thống kê hệ thống
- Auto-backup sau các thay đổi
- Logging cho audit trail
- Validation và error handling
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging

from models.card import ParkingCard
from utils.file_manager import FileManager
from config.config import CARDS_FILE, UNKNOWN_CARDS_FILE

logger = logging.getLogger(__name__)

class CardService:
    """
    Service class xử lý tất cả business logic liên quan đến parking cards
    
    Sử dụng lazy loading cho backup_service và log_service để tránh circular imports
    """
    def __init__(self):
        self.file_manager = FileManager()
        # Lazy loading để tránh circular import
        self._backup_service = None
        self._log_service = None
        
    @property
    def backup_service(self):
        if self._backup_service is None:
            from services.backup_service import BackupService
            self._backup_service = BackupService()
        return self._backup_service
    
    @property 
    def log_service(self):
        if self._log_service is None:
            from services.card_log_service import CardLogService
            self._log_service = CardLogService()
        return self._log_service
    
    def _auto_backup_if_needed(self, reason: str = "auto"):
        """Tự động backup sau các thay đổi quan trọng"""
        try:
            success, message = self.backup_service.create_manual_backup(reason)
            if success:
                logger.debug(f"Auto backup created: {reason}")
        except Exception as e:
            logger.warning(f"Auto backup failed: {e}")
        
    def get_all_cards(self) -> Dict[str, ParkingCard]:
        try:
            success, raw_data = self.file_manager.read_json(CARDS_FILE, default_value={})
            if not success:
                return {}
            return self._parse_cards_from_dict(raw_data)
        except Exception as e:
            logger.error(f"Error reading cards: {e}")
            return {}
    
    def _parse_cards_from_dict(self, data: Dict) -> Dict[str, ParkingCard]:
        try:
            cards_dict = {}
            if isinstance(data, dict):
                if 'cards' in data:
                    cards_data = data['cards']
                else:
                    cards_data = data
                for uid, card_data in cards_data.items():
                    if isinstance(card_data, dict) and 'uid' in card_data:
                        try:
                            card = ParkingCard.from_dict(card_data)
                            cards_dict[uid] = card
                        except Exception as e:
                            logger.warning(f"Error parsing card {uid}: {e}")
                            continue
            return cards_dict
        except Exception as e:
            logger.error(f"Error parsing cards dict: {e}")
            return {}
            
    def get_card(self, uid: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        try:
            cards = self.get_all_cards()
            if uid in cards:
                card = cards[uid]
                return True, card.to_dict()
            else:
                return False, None
        except Exception as e:
            logger.error(f"Error getting card {uid}: {e}")
            return False, None
            
    def create_card(self, uid: str, name: str = '', status: int = 0) -> Tuple[bool, str, Optional[ParkingCard]]:
        try:
            cards_dict = self.get_all_cards()
            if uid in cards_dict:
                error_msg = f"Thẻ {uid} đã tồn tại"
                logger.warning(error_msg)
                return False, error_msg, None
            
            new_card = ParkingCard(uid=uid, name=name, status=status)
            cards_dict[uid] = new_card
            
            cards_data = {}
            for card_uid, card_obj in cards_dict.items():
                cards_data[card_uid] = card_obj.to_dict()
            
            success, message = self.file_manager.write_json(CARDS_FILE, cards_data, max_backups=5)
            
            if success:
                try:
                    from services.card_log_service import LogAction
                    self.log_service.add_log(uid, LogAction.CARD_CREATED, {"initial_status": status})
                except Exception as e:
                    logger.warning(f"Failed to log card creation: {e}")
                
                logger.info(f"Card {uid} created successfully with status {status}")
                return True, f"Thẻ {uid} đã được thêm thành công", new_card
            else:
                error_msg = f"Lỗi lưu thẻ {uid}"
                logger.error(error_msg)
                return False, error_msg, None
        except Exception as e:
            error_msg = f"Lỗi tạo thẻ {uid}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
    def delete_card(self, uid: str) -> Tuple[bool, str]:
        try:
            cards_dict = self.get_all_cards()
            if uid not in cards_dict:
                error_msg = f"Thẻ {uid} không tồn tại"
                logger.warning(error_msg)
                return False, error_msg
            
            del cards_dict[uid]
            
            cards_data = {}
            for card_uid, card_obj in cards_dict.items():
                cards_data[card_uid] = card_obj.to_dict()
            
            success, message = self.file_manager.write_json(CARDS_FILE, cards_data, max_backups=5)
            
            if success:
                try:
                    from services.card_log_service import LogAction
                    self.log_service.add_log(uid, LogAction.CARD_DELETED, {"reason": "manual_deletion"})
                except Exception as e:
                    logger.warning(f"Failed to log card deletion: {e}")
                
                logger.info(f"Card {uid} deleted successfully")
                return True, f"Thẻ {uid} đã được xóa thành công"
            else:
                error_msg = f"Lỗi xóa thẻ {uid}"
                logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Lỗi xóa thẻ {uid}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
    def update_card_status(self, uid: str, new_status: int) -> Tuple[bool, str, Optional[Dict]]:
        try:
            cards_dict = self.get_all_cards()
            if uid not in cards_dict:
                error_msg = f"Thẻ {uid} không tồn tại"
                logger.warning(error_msg)
                return False, error_msg, None
            
            card = cards_dict[uid]
            old_status = card.status
            
            update_result = card.update_status(new_status)
            if not update_result["success"]:
                return False, update_result["message"], None
            
            cards_data = {}
            for card_uid, card_obj in cards_dict.items():
                cards_data[card_uid] = card_obj.to_dict()
            
            success, message = self.file_manager.write_json(CARDS_FILE, cards_data, max_backups=5)
            
            if success:
                try:
                    from services.card_log_service import LogAction
                    if new_status == 1:
                        self.log_service.add_log(uid, LogAction.CARD_ENTRY, {"previous_status": old_status, "new_status": new_status})
                    else:
                        self.log_service.add_log(uid, LogAction.CARD_EXIT, {"previous_status": old_status, "new_status": new_status})
                except Exception as e:
                    logger.warning(f"Failed to log status update: {e}")
                
                message = f"Cập nhật trạng thái thẻ {uid} thành công"
                logger.info(message)
                return True, message, card.to_dict()
            else:
                error_msg = f"Lỗi lưu trạng thái thẻ {uid}"
                logger.error(error_msg)
                return False, error_msg, None
        except Exception as e:
            error_msg = f"Lỗi cập nhật trạng thái thẻ {uid}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
    def get_statistics(self) -> Dict[str, Any]:
        try:
            cards = self.get_all_cards()
            total_cards = len(cards)
            inside_count = sum(1 for card in cards.values() if card.status == 1)
            outside_count = total_cards - inside_count
            
            return {
                "total_cards": total_cards,
                "inside_parking": inside_count,
                "outside_parking": outside_count,
                "occupancy_rate": (inside_count / total_cards * 100) if total_cards > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
            
    def add_unknown_card(self, uid: str, metadata: Dict[str, Any] = None) -> Tuple[bool, str]:
        try:
            unknown_cards = self.get_unknown_cards()
            normalized_uid = uid.upper().strip()
            for card in unknown_cards:
                if card.get("uid") == normalized_uid:
                    return True, f"Unknown card {uid} already exists"
            
            try:
                from services.card_log_service import LogAction
                self.log_service.add_log(uid, LogAction.UNKNOWN_CARD, metadata or {})
            except Exception as e:
                logger.warning(f"Failed to log unknown card: {e}")
            
            unknown_card = {
                "uid": normalized_uid,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **(metadata or {})
            }
            
            unknown_cards.append(unknown_card)
            data = {"unknown_cards": unknown_cards}
            success, message = self.file_manager.write_json(UNKNOWN_CARDS_FILE, data, max_backups=5)
            
            if success:
                logger.info(f"Added unknown card: {uid}")
                return True, f"Unknown card {uid} added successfully"
            else:
                logger.error(f"Failed to save unknown card: {message}")
                return False, f"Failed to save unknown card: {message}"
        except Exception as e:
            error_msg = f"Error adding unknown card {uid}: {e}"
            logger.error(error_msg)
            return False, error_msg

    def get_unknown_cards(self) -> List[Dict[str, Any]]:
        try:
            success, data = self.file_manager.read_json(UNKNOWN_CARDS_FILE, default_value={"unknown_cards": []})
            if success:
                return data.get("unknown_cards", [])
            return []
        except Exception as e:
            logger.error(f"Failed to load unknown cards: {e}")
            return []
    
    def remove_unknown_card(self, uid: str) -> Tuple[bool, str]:
        try:
            unknown_cards = self.get_unknown_cards()
            normalized_uid = uid.upper().strip()
            updated_cards = [card for card in unknown_cards if card.get("uid") != normalized_uid]
            
            if len(updated_cards) == len(unknown_cards):
                return True, f"Unknown card {uid} was not in list"
            
            data = {"unknown_cards": updated_cards}
            success, message = self.file_manager.write_json(UNKNOWN_CARDS_FILE, data, max_backups=5)
            
            if success:
                logger.info(f"Removed unknown card: {uid}")
                return True, f"Unknown card {uid} removed successfully"
            else:
                logger.error(f"Failed to remove unknown card: {message}")
                return False, f"Failed to remove unknown card: {message}"
        except Exception as e:
            error_msg = f"Failed to remove unknown card {uid}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def clear_unknown_cards(self) -> bool:
        """Clear all unknown cards from the system"""
        try:
            data = {"unknown_cards": []}
            success, message = self.file_manager.write_json(UNKNOWN_CARDS_FILE, data, max_backups=5)
            
            if success:
                logger.info("Cleared all unknown cards")
                return True
            else:
                logger.error(f"Failed to clear unknown cards: {message}")
                return False
        except Exception as e:
            error_msg = f"Failed to clear unknown cards: {e}"
            logger.error(error_msg)
            return False
