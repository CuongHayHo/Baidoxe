"""
Flask Application Factory - Main Flask app setup
Tạo và cấu hình Flask application với tất cả components
"""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import JWTManager

# Import configuration
from config.config import config, DEBUG_MODE, FRONTEND_BUILD_DIR
from config.cors import init_cors

# Import database
from flask_sqlalchemy import SQLAlchemy

# Import API blueprints
from api.cards import cards_bp
from api.parking_slots import parking_slots_bp
from api.system import system_bp
from api.auth import auth_bp
from api.users import users_bp

# Import scheduled tasks
from services.scheduled_tasks import scheduled_tasks

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler('backend.log')  # Uncomment for file logging
    ]
)

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

def _create_user_model(db_instance):
    """Create SQLAlchemy User model and register it in models module"""
    from datetime import datetime
    import models
    
    # Check if already created by looking at __tablename__ attribute
    if hasattr(models.User, '__tablename__'):
        return
    
    class User(db_instance.Model):
        """User model for admin and staff roles"""
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}
        
        id = db_instance.Column(db_instance.Integer, primary_key=True)
        username = db_instance.Column(db_instance.String(80), unique=True, nullable=False, index=True)
        password_hash = db_instance.Column(db_instance.String(255), nullable=False)
        email = db_instance.Column(db_instance.String(120), unique=True, nullable=True)
        full_name = db_instance.Column(db_instance.String(120), nullable=True)
        role = db_instance.Column(db_instance.String(20), default='staff', nullable=False)
        is_active = db_instance.Column(db_instance.Boolean, default=True, nullable=False)
        created_at = db_instance.Column(db_instance.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db_instance.Column(db_instance.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
        
        def __repr__(self):
            return f'<User {self.username}>'
    
    # Register in models module
    models.User = User
    models.db = db_instance

def create_app(config_name='default'):
    """
    Application factory pattern to create Flask app
    
    Args:
        config_name: Configuration environment (development, production, default)
        
    Returns:
        Configured Flask application instance
    """
    logger.info(f"Creating Flask app with config: {config_name}")
    
    # Create Flask app instance with frontend paths
    frontend_build = Path(__file__).parent.parent / "frontend" / "build"
    app = Flask(__name__, 
                static_folder=str(frontend_build / "static"),
                template_folder=str(frontend_build))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Disable automatic trailing slash redirect
    app.url_map.strict_slashes = False
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create User model now that db is initialized with app
    _create_user_model(db)
    
    # Pre-initialize SQLAlchemy models cache to avoid metadata conflicts later
    from models.models_cache import get_sqlalchemy_models
    with app.app_context():
        get_sqlalchemy_models()  # Initialize cache on first call
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS
    init_cors(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Setup request/response logging
    setup_request_logging(app)
    
    # Setup static file serving for frontend
    setup_frontend_serving(app)
    
    # Add health check endpoint
    setup_health_endpoints(app)
    
    # Start background scheduler for auto backup and maintenance
    setup_scheduler(app)
    
    logger.info("Flask app created successfully")
    return app

def setup_scheduler(app):
    """Setup and start background scheduler"""
    try:
        # Start scheduler when app is ready
        scheduled_tasks.start_scheduler()
        logger.info("Background scheduler started with Flask app")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

def register_blueprints(app):
    """Register all API blueprints"""
    logger.info("Registering API blueprints...")
    
    # Register API blueprints
    app.register_blueprint(cards_bp)
    app.register_blueprint(parking_slots_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    logger.info("API blueprints registered successfully")

def setup_error_handlers(app):
    """Setup global error handlers"""
    logger.info("Setting up error handlers...")
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            "success": False,
            "error": "Not Found",
            "message": "Endpoint không tồn tại",
            "status_code": 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({
            "success": False,
            "error": "Method Not Allowed",
            "message": "Phương thức HTTP không được hỗ trợ",
            "status_code": 405,
            "allowed_methods": list(error.valid_methods) if hasattr(error, 'valid_methods') else []
        }), 405
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        """Handle 415 errors"""
        logger.warning(f"Unsupported media type error: {error}")
        return jsonify({
            "success": False,
            "error": "Unsupported Media Type",
            "message": "Content-Type không được hỗ trợ",
            "status_code": 415,
            "expected_content_type": "application/json"
        }), 415
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Lỗi server nội bộ",
            "status_code": 500
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all HTTP exceptions"""
        return jsonify({
            "success": False,
            "error": error.name,
            "message": error.description,
            "status_code": error.code
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exceptions"""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Unexpected Error",
            "message": "Đã xảy ra lỗi không mong muốn",
            "status_code": 500
        }), 500

def setup_request_logging(app):
    """Setup request/response logging for debugging"""
    
    @app.before_request
    def log_request_info():
        """Log incoming request details"""
        if DEBUG_MODE:
            logger.debug(f"Request: {request.method} {request.url}")
            # Only log JSON for methods that expect body and avoid parsing errors
            if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                try:
                    if request.json:
                        logger.debug(f"Request body: {request.json}")
                except Exception:
                    # Don't fail request due to logging issues
                    pass
    
    @app.after_request
    def log_response_info(response):
        """Log response details and add common headers"""
        if DEBUG_MODE:
            logger.debug(f"Response: {response.status_code}")
        
        # Add common security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

def setup_frontend_serving(app):
    """Setup static file serving for React frontend"""
    logger.info("Setting up frontend file serving...")
    
    # Serve React build files
    @app.route('/')
    def serve_frontend():
        """Serve React app index.html"""
        try:
            if FRONTEND_BUILD_DIR.exists():
                return send_from_directory(FRONTEND_BUILD_DIR, 'index.html')
            else:
                return jsonify({
                    "message": "Parking Management System API",
                    "version": "1.0.0",
                    "status": "running",
                    "frontend_available": False,
                    "note": "Frontend build not found. Please build the React app."
                }), 200
        except Exception as e:
            logger.error(f"Error serving frontend: {e}")
            return jsonify({
                "error": "Frontend serving error",
                "message": str(e)
            }), 500
    
    @app.route('/<path:filename>')
    def serve_static_files(filename):
        """Serve static files (CSS, JS, images) or React routes"""
        try:
            if FRONTEND_BUILD_DIR.exists():
                # Try to serve actual files first (CSS, JS, images)
                file_path = FRONTEND_BUILD_DIR / filename
                if file_path.exists() and file_path.is_file():
                    return send_from_directory(FRONTEND_BUILD_DIR, filename)
                
                # If not a real file, check if it's a React Router path
                react_routes = ['dashboard', 'cards', 'parking', 'logs', 'admin']
                if filename in react_routes or '/' in filename:
                    # Serve index.html for React Router paths
                    return send_from_directory(FRONTEND_BUILD_DIR, 'index.html')
                
                # Not found
                return jsonify({
                    "error": "File not found",
                    "message": f"File '{filename}' not found"
                }), 404
            else:
                # Fallback for API endpoints not caught by blueprints
                return jsonify({
                    "error": "File not found", 
                    "message": f"Frontend build not available"
                }), 404
        except Exception as e:
            logger.error(f"Error serving static file {filename}: {e}")
            return jsonify({
                "error": "Static file error",
                "message": str(e)
            }), 500

def setup_health_endpoints(app):
    """Setup health check and info endpoints"""
    logger.info("Setting up health endpoints...")
    
    @app.route('/health')
    def health_check():
        """Quick health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Parking Management System API is running"
        }), 200
    
    @app.route('/api')
    def api_info():
        """API information endpoint"""
        return jsonify({
            "name": "Parking Management System API",
            "version": "1.0.0",
            "description": "Backend API cho hệ thống quản lý bãi đỗ xe với RFID và ESP32",
            "endpoints": {
                "cards": "/api/cards",
                "parking_slots": "/api/parking-slots", 
                "system": "/api/system",
                "health": "/health"
            },
            "documentation": {
                "cards_api": "Quản lý thẻ RFID và trạng thái đỗ xe",
                "parking_slots_api": "Dữ liệu cảm biến ESP32 và quản lý slots",
                "system_api": "Thông tin hệ thống và health checks"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    
    @app.route('/api/endpoints')
    def list_endpoints():
        """List all available API endpoints"""
        endpoints = []
        for rule in app.url_map.iter_rules():
            endpoints.append({
                "endpoint": rule.rule,
                "methods": list(rule.methods - {'HEAD', 'OPTIONS'}),
                "description": rule.endpoint.replace('_', ' ').title()
            })
        
        return jsonify({
            "total_endpoints": len(endpoints),
            "endpoints": sorted(endpoints, key=lambda x: x['endpoint']),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

def setup_data_directories():
    """Ensure required data directories exist"""
    from config.config import DATA_DIR
    
    try:
        # Create data directory if it doesn't exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ensured: {DATA_DIR}")
        
        # Initialize empty JSON files if they don't exist
        from config.config import CARDS_FILE, UNKNOWN_CARDS_FILE
        
        if not CARDS_FILE.exists():
            import json
            with open(CARDS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info(f"Created empty cards file: {CARDS_FILE}")
        
        if not UNKNOWN_CARDS_FILE.exists():
            import json
            with open(UNKNOWN_CARDS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info(f"Created empty unknown cards file: {UNKNOWN_CARDS_FILE}")
            
    except Exception as e:
        logger.error(f"Error setting up data directories: {e}")
        raise

# Application factory for different environments
def create_development_app():
    """Create app for development environment"""
    setup_data_directories()
    return create_app('development')

def create_production_app():
    """Create app for production environment"""
    setup_data_directories()
    return create_app('production')

# Default app instance
app = create_development_app()

if __name__ == '__main__':
    # This allows running the app directly with: python app.py
    logger.info("Starting Flask app in development mode...")
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )