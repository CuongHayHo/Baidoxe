"""
CORS configuration for frontend-backend communication
"""
from flask_cors import CORS

def init_cors(app):
    """Initialize CORS for the Flask app"""
    CORS(app, 
         origins=[
             "http://localhost:3000",      # React development
             "http://127.0.0.1:3000",     # React development  
             "http://localhost:5000",      # Production build
             "http://127.0.0.1:5000",     # Production build
             "http://192.168.4.3:5000",   # Network access
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True
    )
    return app