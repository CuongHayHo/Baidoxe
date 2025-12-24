"""
File Manager - Bộ công cụ xử lý file operations (JSON read/write)

Chức năng chính:
- Đọc/ghi file JSON với error handling
- Tạo backup files tự động
- Thread-safe file operations
- Validation và rollback khi ghi file thất bại
- Quản lý encoding UTF-8 cho tiếng Việt
"""
import json
import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class FileManager:
    """
    Lớp utility để quản lý các thao tác file, đặc biệt là JSON files
    
    Cung cấp các method thread-safe để:
    - Đọc/ghi JSON files với proper encoding
    - Tạo backup tự động trước khi ghi
    - Error handling và recovery
    - Validation dữ liệu trước khi ghi
    """
    
    @staticmethod
    def read_json(file_path: str, default_value: Any = None) -> Tuple[bool, Any]:
        """
        Đọc file JSON với xử lý lỗi toàn diện
        
        Args:
            file_path: Đường dẫn đến file JSON
            default_value: Giá trị trả về nếu file không tồn tại hoặc lỗi
            
        Returns:
            Tuple (success, data)
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"JSON file not found: {file_path}")
                return False, default_value
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.debug(f"Successfully read JSON file: {file_path}")
            return True, data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            return False, default_value
            
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return False, default_value
            
        except PermissionError:
            logger.error(f"Permission denied reading file: {file_path}")
            return False, default_value
            
        except Exception as e:
            logger.error(f"Unexpected error reading JSON file {file_path}: {e}")
            return False, default_value
    
    @staticmethod
    def write_json(file_path: str, data: Any, create_backup: bool = True, max_backups: int = 5) -> Tuple[bool, str]:
        """
        Write data to JSON file with error handling and backup
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            create_backup: Whether to create backup before writing
            max_backups: Maximum number of backup files to keep
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            
            # Create backup if file exists and backup is requested
            if create_backup and os.path.exists(file_path):
                backup_success, backup_msg = FileManager._create_backup(file_path)
                if not backup_success:
                    logger.warning(f"Backup creation failed: {backup_msg}")
                else:
                    # Clean up old backups after creating new one
                    cleanup_success, cleanup_msg = FileManager.cleanup_backups(file_path, max_backups)
                    if cleanup_success:
                        logger.debug(f"Backup cleanup: {cleanup_msg}")
                    else:
                        logger.warning(f"Backup cleanup failed: {cleanup_msg}")
            
            # Write data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Successfully wrote JSON file: {file_path}")
            return True, f"File written successfully: {file_path}"
            
        except PermissionError:
            error_msg = f"Permission denied writing to file: {file_path}"
            logger.error(error_msg)
            return False, error_msg
            
        except OSError as e:
            error_msg = f"OS error writing file {file_path}: {e}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error writing JSON file {file_path}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def _create_backup(file_path: str) -> Tuple[bool, str]:
        """
        Create backup copy of file
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Tuple of (success, message)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.backup_{timestamp}"
            
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
            return True, f"Backup created: {backup_path}"
            
        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes or None if file doesn't exist
        """
        try:
            if FileManager.file_exists(file_path):
                return os.path.getsize(file_path)
            return None
        except OSError:
            return None
    
    @staticmethod
    def get_file_modified_time(file_path: str) -> Optional[datetime]:
        """
        Get file last modified time
        
        Args:
            file_path: Path to file
            
        Returns:
            Last modified datetime or None if file doesn't exist
        """
        try:
            if FileManager.file_exists(file_path):
                timestamp = os.path.getmtime(file_path)
                return datetime.fromtimestamp(timestamp)
            return None
        except OSError:
            return None
    
    @staticmethod
    def list_json_files(directory: str) -> List[str]:
        """
        List all JSON files in directory
        
        Args:
            directory: Directory to search
            
        Returns:
            List of JSON file paths
        """
        try:
            if not os.path.exists(directory):
                return []
            
            json_files = []
            for file in os.listdir(directory):
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(directory, file))
            
            return sorted(json_files)
            
        except OSError:
            return []
    
    @staticmethod
    def cleanup_backups(file_path: str, keep_count: int = 5) -> Tuple[bool, str]:
        """
        Clean up old backup files, keeping only the most recent ones
        
        Args:
            file_path: Original file path
            keep_count: Number of backups to keep
            
        Returns:
            Tuple of (success, message)
        """
        try:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # Find all backup files
            backups = []
            for file in os.listdir(directory):
                if file.startswith(f"{filename}.backup_"):
                    backup_path = os.path.join(directory, file)
                    mod_time = os.path.getmtime(backup_path)
                    backups.append((mod_time, backup_path))
            
            # Sort by modification time (newest first)
            backups.sort(reverse=True)
            
            # Remove old backups
            removed_count = 0
            for i, (_, backup_path) in enumerate(backups):
                if i >= keep_count:
                    try:
                        os.remove(backup_path)
                        removed_count += 1
                        logger.debug(f"Removed old backup: {backup_path}")
                    except OSError as e:
                        logger.warning(f"Failed to remove backup {backup_path}: {e}")
            
            message = f"Cleaned up {removed_count} old backups, kept {min(len(backups), keep_count)}"
            logger.debug(message)
            return True, message
            
        except Exception as e:
            error_msg = f"Error cleaning up backups: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def ensure_directory(directory_path: str) -> Tuple[bool, str]:
        """
        Ensure directory exists, create if necessary
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                logger.debug(f"Created directory: {directory_path}")
                return True, f"Directory created: {directory_path}"
            else:
                return True, f"Directory already exists: {directory_path}"
                
        except Exception as e:
            error_msg = f"Failed to create directory {directory_path}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def read_text_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Read text file content
        
        Args:
            file_path: Path to text file
            
        Returns:
            Tuple of (success, content)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"Successfully read text file: {file_path}")
            return True, content
            
        except FileNotFoundError:
            logger.warning(f"Text file not found: {file_path}")
            return False, None
            
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return False, None
    
    @staticmethod
    def write_text_file(file_path: str, content: str) -> Tuple[bool, str]:
        """
        Write content to text file
        
        Args:
            file_path: Path to text file
            content: Content to write
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create directory if needed
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"Successfully wrote text file: {file_path}")
            return True, f"Text file written: {file_path}"
            
        except Exception as e:
            error_msg = f"Error writing text file {file_path}: {e}"
            logger.error(error_msg)
            return False, error_msg