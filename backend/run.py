#!/usr/bin/env python3
"""
Application Runner - Entry point for running the Flask application
Điểm khởi chạy chính cho Flask application
"""
import sys
import os
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_development_app, create_production_app
from config.config import API_HOST, API_PORT, DEBUG_MODE

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_development():
    """Run application in development mode"""
    logger.info("🚀 Starting Parking Management System - Development Mode")
    logger.info(f"📍 Server will run at: http://{API_HOST}:{API_PORT}")
    logger.info("🔧 Debug mode: ON")
    logger.info("🌐 CORS enabled for frontend development")
    
    try:
        # Create development app
        app = create_development_app()
        
        # Run with Flask development server
        app.run(
            host=API_HOST,
            port=API_PORT,
            debug=DEBUG_MODE,
            threaded=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

def run_production():
    """Run application in production mode"""
    logger.info("🚀 Starting Parking Management System - Production Mode")
    logger.info(f"📍 Server will run at: http://{API_HOST}:{API_PORT}")
    logger.info("🔒 Debug mode: OFF")
    
    try:
        # Create production app
        app = create_production_app()
        
        # Check if gunicorn is available for production
        try:
            import gunicorn
            logger.info("🦄 Gunicorn available - recommended for production")
            logger.info("💡 Run with: gunicorn -w 4 -b 0.0.0.0:5000 run:app")
        except ImportError:
            logger.warning("⚠️  Gunicorn not installed - using Flask dev server")
            logger.warning("💡 Install with: pip install gunicorn")
        
        # Run with Flask server (not recommended for production)
        app.run(
            host=API_HOST,
            port=API_PORT,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

def show_system_info():
    """Display system information"""
    print("🏢 Parking Management System Backend")
    print("=" * 50)
    print("📋 System Information:")
    print(f"  🐍 Python: {sys.version}")
    print(f"  📁 Backend directory: {backend_dir}")
    print(f"  🌐 API endpoint: http://{API_HOST}:{API_PORT}")
    print(f"  🔧 Debug mode: {DEBUG_MODE}")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    dependencies = ['flask', 'flask_cors', 'requests']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - Not installed")
    
    # Check configuration
    print("\n⚙️  Configuration:")
    try:
        from config.config import ESP32_IP, ESP32_PORT, CARDS_FILE
        print(f"  📡 ESP32: {ESP32_IP}:{ESP32_PORT}")
        print(f"  📄 Cards file: {CARDS_FILE}")
        print(f"  🐛 Debug: {DEBUG_MODE}")
    except ImportError as e:
        print(f"  ❌ Configuration error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['dev', 'development']:
            run_development()
        elif command in ['prod', 'production']:
            run_production()
        elif command in ['info', 'status']:
            show_system_info()
        elif command in ['help', '-h', '--help']:
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
            sys.exit(1)
    else:
        # Default to development mode
        run_development()

def print_help():
    """Print help information"""
    print("🏢 Parking Management System Backend")
    print("=" * 50)
    print("Usage: python run.py [command]")
    print("\nCommands:")
    print("  dev, development    Run in development mode (default)")
    print("  prod, production    Run in production mode")
    print("  info, status        Show system information")
    print("  help                Show this help message")
    print("\nExamples:")
    print("  python run.py                 # Run in development mode")
    print("  python run.py dev             # Run in development mode")
    print("  python run.py prod            # Run in production mode")
    print("  python run.py info            # Show system info")
    print("\nFor production deployment:")
    print("  pip install gunicorn")
    print("  gunicorn -w 4 -b 0.0.0.0:5000 run:app")

# Create app instance for gunicorn
app = create_production_app()

if __name__ == '__main__':
    main()