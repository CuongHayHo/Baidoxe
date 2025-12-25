"""
Configuration Management - Quản lý cấu hình cho backend hệ thống bãi đỗ xe

Chứa tất cả cấu hình:
- File paths và directories
- Network configuration (API server, ESP32, UNO R4)
- Auto IP detection cho UNO R4 WiFi network
- Mock server settings cho testing
- Flask app configurations
- Database configuration
"""
import os
from pathlib import Path

# Thư mục gốc của project
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "parking_system.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Files lưu dữ liệu
DATA_DIR = BASE_DIR / "data"
CARDS_FILE = DATA_DIR / "cards.json"          # File lưu thông tin các thẻ đã đăng ký
UNKNOWN_CARDS_FILE = DATA_DIR / "unknown_cards.json"  # File lưu các thẻ lạ

# Cấu hình mạng
def detect_api_host():
    """Tự động phát hiện IP interface kết nối với UNO R4 WiFi"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.4.2", 80))  # Lựa chọn 1: WiFi AP
        host = s.getsockname()[0]
        s.close()
        print(f"🎯 Server sẽ chạy trên: {host}")
        return host
    except:
        print("⚠️ Không phát hiện UNO R4, sử dụng 0.0.0.0")
        return "0.0.0.0"
    
    # Lựa chọn 2: Local WiFi - uncomment dòng dưới và comment hàm trên
    # return "192.168.1.50"  # // IP cụ thể của PC chạy backend trên local WiFi

API_HOST = "0.0.0.0"  # Chạy trên tất cả interface (localhost + 192.168.x.x đều kết nối được)
API_PORT = 5000
DEBUG_MODE = True

# ESP32 configuration
# Lựa chọn 1: WiFi AP (UNO R4 phát WiFi)
ESP32_IP = "192.168.4.5"
ESP32_PORT = 80
ESP32_TIMEOUT = 10
DETECTION_THRESHOLD = 10  # cm - threshold for parking detection

# Lựa chọn 2: Local WiFi (kết nối router có Internet)
# ESP32_IP = "192.168.1.100"      # // IP của ESP32 trong local WiFi
# ESP32_PORT = 80
# ESP32_TIMEOUT = 10
# DETECTION_THRESHOLD = 10

# Cấu hình backup và logging
BACKUP_INTERVAL = 3600  # 1 giờ
MAX_BACKUPS = 24       # Giữ lại 24 backup (1 ngày)

# UNO R4 WiFi configuration
# Lựa chọn 1: WiFi AP (UNO R4 phát WiFi)
UNO_R4_IP = "192.168.4.2"  # IP tĩnh của UNO R4
UNO_R4_AP_SSID = "UNO-R4-AP"

# Lựa chọn 2: Local WiFi (kết nối router)
# UNO_R4_IP = "192.168.1.101"  # // IP của UNO R4 trong local WiFi

# Frontend configuration
FRONTEND_BUILD_DIR = BASE_DIR.parent / "frontend" / "build"

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = DEBUG_MODE
    HOST = API_HOST
    PORT = API_PORT
    # Database configuration
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key'
    JWT_EXPIRATION_HOURS = 24
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}