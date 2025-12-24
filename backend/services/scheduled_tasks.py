"""
Scheduled Tasks - Hệ thống tự động chạy các tác vụ theo lịch

Chức năng chính:
- Tự động backup dữ liệu mỗi giờ
- Cleanup log cũ và temporary files
- Health check ESP32 connection
- Database maintenance tasks
- Performance monitoring
- Error recovery và retry logic
"""
import threading
import time
import logging
from datetime import datetime, timezone
from typing import Optional

from services.backup_service import BackupService
from services.card_log_service import CardLogService
from services.esp32_service import ESP32Service

logger = logging.getLogger(__name__)

class ScheduledTasks:
    """
    Lớp service chạy các tác vụ nền theo lịch trình
    
    Quản lý:
    - Background thread để chạy scheduler
    - Interval timing cho từng loại task
    - Error handling và recovery
    - Thread safety và graceful shutdown
    """
    
    def __init__(self):
        """Khởi tạo scheduled tasks với các service dependencies"""
        self.backup_service = BackupService()
        self.log_service = CardLogService()
        self.esp32_service = ESP32Service()
        
        # Quản lý thread
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_scheduler = threading.Event()
        
        # Khoảng thời gian chạy task (tính bằng giây)
        self.backup_interval = 3600  # 1 giờ = 3600 giây
        self.cleanup_interval = 86400  # 1 ngày = 86400 giây  
        self.esp32_poll_interval = 1800  # 30 phút = 1800 giây
        
        # Timestamp lần chạy cuối của mỗi task
        self.last_backup_time = 0
        self.last_cleanup_time = 0
        self.last_esp32_poll_time = 0
        
        logger.info("ScheduledTasks initialized")
    
    def start_scheduler(self):
        """Khởi động background scheduler thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Scheduler already running")
            return
        
        self.stop_scheduler.clear()
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Background scheduler started")
    
    def stop_scheduler_tasks(self):
        """Dừng background scheduler một cách graceful"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.stop_scheduler.set()
            self.scheduler_thread.join(timeout=5)
            logger.info("Background scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop running in background thread"""
        logger.info("Scheduler loop started")
        
        while not self.stop_scheduler.is_set():
            try:
                current_time = time.time()
                
                # Check if it's time for hourly backup
                if current_time - self.last_backup_time >= self.backup_interval:
                    self._run_hourly_backup()
                    self.last_backup_time = current_time
                
                # Check if it's time for ESP32 polling (30 minutes)
                if current_time - self.last_esp32_poll_time >= self.esp32_poll_interval:
                    self._run_esp32_polling()
                    self.last_esp32_poll_time = current_time
                
                # Check if it's time for daily cleanup
                if current_time - self.last_cleanup_time >= self.cleanup_interval:
                    self._run_daily_cleanup()
                    self.last_cleanup_time = current_time
                
                # Sleep for 60 seconds before next check
                if not self.stop_scheduler.wait(60):
                    continue  # Continue loop if not stopped
                else:
                    break  # Exit loop if stop signal received
                    
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)  # Wait before retrying
        
        logger.info("Scheduler loop ended")
    
    def _run_hourly_backup(self):
        """Run hourly backup task"""
        try:
            logger.info("Running hourly backup task")
            
            success, message = self.backup_service.create_hourly_backup()
            
            if success:
                logger.info("Hourly backup completed successfully")
            else:
                logger.warning(f"Hourly backup failed: {message}")
                
        except Exception as e:
            logger.error(f"Hourly backup task error: {e}")
    
    def _run_esp32_polling(self):
        """Run ESP32 sensor data polling (every 30 minutes)"""
        try:
            logger.info("Running ESP32 polling task (30-minute interval)")
            
            # Poll ESP32 for current sensor data using correct method
            success, raw_data, slots_data = self.esp32_service.get_parking_slots()
            
            if success and slots_data:
                logger.info(f"ESP32 polling successful: {slots_data.total_sensors} sensors, "
                           f"{len(slots_data.slots)} slots")
                # Data automatically cached by ESP32Service
            else:
                logger.warning(f"ESP32 polling failed: {raw_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"ESP32 polling task error: {e}")
    
    def _run_daily_cleanup(self):
        """Run daily cleanup tasks"""
        try:
            logger.info("Running daily cleanup tasks")
            
            # Cleanup old backup files (done automatically in BackupService)
            stats = self.backup_service.get_backup_stats()
            logger.info(f"Backup stats: {stats.get('total_backups', 0)} files, "
                       f"{stats.get('total_size_mb', 0)} MB")
            
            # Log cleanup statistics
            log_stats = self.log_service.get_statistics()
            logger.info(f"Log stats: {log_stats.get('total_logs', 0)} entries, "
                       f"file size: {log_stats.get('log_file_size', 0)} bytes")
            
            logger.info("Daily cleanup completed")
            
        except Exception as e:
            logger.error(f"Daily cleanup task error: {e}")
    
    def force_backup_now(self) -> tuple[bool, str]:
        """
        Force immediate backup (manual trigger)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info("Force backup requested")
            return self.backup_service.create_manual_backup("force_backup")
        except Exception as e:
            error_msg = f"Force backup failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_scheduler_status(self) -> dict:
        """
        Get current scheduler status and next run times
        
        Returns:
            Dictionary with scheduler status info
        """
        current_time = time.time()
        
        # Calculate next run times
        next_backup = self.last_backup_time + self.backup_interval
        next_cleanup = self.last_cleanup_time + self.cleanup_interval
        next_esp32_poll = self.last_esp32_poll_time + self.esp32_poll_interval
        
        status = {
            "scheduler_running": (
                self.scheduler_thread is not None and 
                self.scheduler_thread.is_alive()
            ),
            "current_time": datetime.now(timezone.utc).isoformat(),
            "backup": {
                "interval_hours": self.backup_interval / 3600,
                "last_run": datetime.fromtimestamp(self.last_backup_time).isoformat() if self.last_backup_time > 0 else None,
                "next_run": datetime.fromtimestamp(next_backup).isoformat() if self.last_backup_time > 0 else "Soon",
                "seconds_until_next": max(0, next_backup - current_time) if self.last_backup_time > 0 else 0
            },
            "esp32_polling": {
                "interval_minutes": self.esp32_poll_interval / 60,
                "last_run": datetime.fromtimestamp(self.last_esp32_poll_time).isoformat() if self.last_esp32_poll_time > 0 else None,
                "next_run": datetime.fromtimestamp(next_esp32_poll).isoformat() if self.last_esp32_poll_time > 0 else "Soon",
                "seconds_until_next": max(0, next_esp32_poll - current_time) if self.last_esp32_poll_time > 0 else 0
            },
            "cleanup": {
                "interval_hours": self.cleanup_interval / 3600,
                "last_run": datetime.fromtimestamp(self.last_cleanup_time).isoformat() if self.last_cleanup_time > 0 else None,
                "next_run": datetime.fromtimestamp(next_cleanup).isoformat() if self.last_cleanup_time > 0 else "Soon",
                "seconds_until_next": max(0, next_cleanup - current_time) if self.last_cleanup_time > 0 else 0
            }
        }
        
        return status

# Global instance
scheduled_tasks = ScheduledTasks()