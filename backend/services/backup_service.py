"""
Backup Service - Tự động backup dữ liệu cards theo giờ
Tự động tạo backup files với timestamp để bảo vệ dữ liệu
"""
import os
import shutil
import logging
from datetime import datetime, timezone
from typing import Tuple, List
from pathlib import Path
import glob

from config.config import CARDS_FILE

logger = logging.getLogger(__name__)

class BackupService:
    """
    Service class for automatic data backup management
    """
    
    def __init__(self):
        """Initialize backup service"""
        # Thư mục chứa backups
        self.backup_dir = Path(CARDS_FILE).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Format timestamp cho backup files
        self.timestamp_format = "%Y%m%d_%H%M%S"
        
        # Số backup files tối đa giữ lại (để tránh đầy ổ cứng)
        self.max_backups = 5  # Chỉ giữ 5 backup files mới nhất
        
        logger.info(f"BackupService initialized - backup dir: {self.backup_dir}")
    
    def create_backup(self, source_file: Path = None, custom_suffix: str = "") -> Tuple[bool, str]:
        """
        Tạo backup file với timestamp
        
        Args:
            source_file: File nguồn để backup (mặc định CARDS_FILE)
            custom_suffix: Hậu tố tùy chỉnh cho tên file
            
        Returns:
            Tuple of (success, backup_file_path)
        """
        try:
            if source_file is None:
                source_file = Path(CARDS_FILE)
            
            # Kiểm tra file nguồn có tồn tại không
            if not source_file.exists():
                error_msg = f"Source file not found: {source_file}"
                logger.warning(error_msg)
                return False, error_msg
            
            # Tạo tên file backup với timestamp
            timestamp = datetime.now().strftime(self.timestamp_format)
            suffix = f"_{custom_suffix}" if custom_suffix else ""
            backup_filename = f"cards_backup_{timestamp}{suffix}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy file
            shutil.copy2(source_file, backup_path)
            
            # Verify backup thành công
            if backup_path.exists() and backup_path.stat().st_size > 0:
                logger.info(f"Backup created successfully: {backup_filename}")
                
                # Cleanup old backups
                self._cleanup_old_backups()
                
                return True, str(backup_path)
            else:
                error_msg = f"Backup verification failed: {backup_path}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def create_hourly_backup(self) -> Tuple[bool, str]:
        """
        Tạo backup theo giờ (auto-scheduled backup)
        
        Returns:
            Tuple of (success, message)
        """
        return self.create_backup(custom_suffix="hourly")
    
    def create_manual_backup(self, reason: str = "manual") -> Tuple[bool, str]:
        """
        Tạo backup thủ công với lý do
        
        Args:
            reason: Lý do tạo backup
            
        Returns:
            Tuple of (success, message)
        """
        return self.create_backup(custom_suffix=f"manual_{reason}")
    
    def _cleanup_old_backups(self) -> None:
        """
        Xóa các backup cũ để tránh đầy ổ cứng
        Giữ lại tối đa self.max_backups files
        """
        try:
            # Tìm tất cả backup files
            backup_pattern = str(self.backup_dir / "cards_backup_*.json")
            backup_files = glob.glob(backup_pattern)
            
            if len(backup_files) <= self.max_backups:
                return  # Không cần cleanup
            
            # Sort theo thời gian modified (cũ nhất trước)
            backup_files.sort(key=lambda f: os.path.getmtime(f))
            
            # Xóa files cũ nhất
            files_to_delete = backup_files[:-self.max_backups]
            deleted_count = 0
            
            for old_file in files_to_delete:
                try:
                    os.remove(old_file)
                    deleted_count += 1
                    logger.debug(f"Deleted old backup: {os.path.basename(old_file)}")
                except Exception as e:
                    logger.warning(f"Failed to delete old backup {old_file}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backup files")
                
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def list_backups(self) -> List[dict]:
        """
        Liệt kê tất cả backup files
        
        Returns:
            List of backup info dictionaries
        """
        try:
            backup_pattern = str(self.backup_dir / "cards_backup_*.json")
            backup_files = glob.glob(backup_pattern)
            
            backups = []
            for backup_file in backup_files:
                file_path = Path(backup_file)
                stat = file_path.stat()
                
                backup_info = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_hourly": "hourly" in file_path.name,
                    "is_manual": "manual" in file_path.name
                }
                backups.append(backup_info)
            
            # Sort theo thời gian tạo (mới nhất trước)
            backups.sort(key=lambda b: b["created_time"], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def restore_from_backup(self, backup_filename: str) -> Tuple[bool, str]:
        """
        Khôi phục dữ liệu từ backup file
        
        Args:
            backup_filename: Tên file backup để restore
            
        Returns:
            Tuple of (success, message)
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                error_msg = f"Backup file not found: {backup_filename}"
                logger.error(error_msg)
                return False, error_msg
            
            # Tạo backup của file hiện tại trước khi restore
            current_backup_success, current_backup_path = self.create_backup(
                custom_suffix="before_restore"
            )
            
            if not current_backup_success:
                logger.warning("Failed to backup current data before restore")
            
            # Copy backup file thành file chính
            shutil.copy2(backup_path, CARDS_FILE)
            
            success_msg = f"Data restored from backup: {backup_filename}"
            logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Restore failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_backup_stats(self) -> dict:
        """
        Lấy thống kê về backups
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backups = self.list_backups()
            
            total_size = sum(b["size_bytes"] for b in backups)
            hourly_count = sum(1 for b in backups if b["is_hourly"])
            manual_count = sum(1 for b in backups if b["is_manual"])
            
            stats = {
                "total_backups": len(backups),
                "hourly_backups": hourly_count,
                "manual_backups": manual_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "backup_directory": str(self.backup_dir),
                "max_backups": self.max_backups,
                "oldest_backup": backups[-1]["created_time"] if backups else None,
                "newest_backup": backups[0]["created_time"] if backups else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get backup stats: {e}")
            return {}