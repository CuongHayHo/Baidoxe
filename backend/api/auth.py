"""
Authentication API endpoints
Các endpoint xác thực: login, register, logout
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import bcrypt
import jwt
from functools import wraps

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_db():
    """Get SQLAlchemy instance"""
    return current_app.extensions.get('sqlalchemy')


def get_user_model():
    """Get User model from models module"""
    import models
    return models.User


def token_required(f):
    """Decorator to check JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user_id = data['user_id']
            current_user_role = data['role']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated(current_user_id, current_user_role, *args, **kwargs):
        if current_user_role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    Expected JSON: {
        "username": "admin",
        "password": "admin123"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400
    
    try:
        db = get_db()
        User = get_user_model()
        
        # Get LoginHistory model
        import models
        LoginHistory = models.LoginHistory
        
        # Get client IP and User-Agent for login history
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            # Record failed login attempt
            failed_login = LoginHistory(
                user_id=None,
                username=data['username'],
                ip_address=client_ip,
                user_agent=user_agent,
                login_status='failed',
                failure_reason='Invalid username'
            )
            db.session.add(failed_login)
            db.session.commit()
            return jsonify({'message': 'Invalid username or password'}), 401
        
        # Verify password - support both bcrypt and werkzeug hashes
        password_valid = False
        if user.password_hash.startswith('$2'):
            # Bcrypt format
            password_valid = bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8'))
        else:
            # Werkzeug format (pbkdf2)
            password_valid = check_password_hash(user.password_hash, data['password'])
        
        if not password_valid:
            # Record failed login attempt
            failed_login = LoginHistory(
                user_id=user.id,
                username=data['username'],
                ip_address=client_ip,
                user_agent=user_agent,
                login_status='failed',
                failure_reason='Invalid password'
            )
            db.session.add(failed_login)
            db.session.commit()
            return jsonify({'message': 'Invalid username or password'}), 401
        
        if not user.is_active:
            # Record failed login attempt for inactive user
            failed_login = LoginHistory(
                user_id=user.id,
                username=data['username'],
                ip_address=client_ip,
                user_agent=user_agent,
                login_status='failed',
                failure_reason='User account is inactive'
            )
            db.session.add(failed_login)
            db.session.commit()
            return jsonify({'message': 'User account is inactive'}), 403
        
        # Generate JWT token
        expiration_time = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS'])
        token = jwt.encode(
            {
                'sub': str(user.id),  # Flask-JWT-Extended requires 'sub' claim for identity
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': expiration_time
            },
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Record successful login
        successful_login = LoginHistory(
            user_id=user.id,
            username=data['username'],
            ip_address=client_ip,
            user_agent=user_agent,
            login_status='success'
        )
        db.session.add(successful_login)
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500


@auth_bp.route('/register', methods=['POST'])
@token_required
@admin_required
def register(current_user_id, current_user_role):
    """
    Register endpoint (Admin only)
    Expected JSON: {
        "username": "user1",
        "password": "password123",
        "email": "user1@parking.com",
        "full_name": "User One",
        "role": "staff"  // or "admin"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400
    
    try:
        db = get_db()
        User = get_user_model()
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400
        
        # Check if email already exists (if provided)
        if data.get('email'):
            existing_email = User.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({'message': 'Email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=data['username'],
            password_hash=password_hash,
            email=data.get('email'),
            full_name=data.get('full_name'),
            role=data.get('role', 'staff'),
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name,
                'role': new_user.role
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Register error: {str(e)}")
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user_id, current_user_role):
    """
    Logout endpoint
    Token is invalidated on client side (remove from localStorage)
    """
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user_id, current_user_role):
    """
    Verify token endpoint - Check if token is still valid
    """
    return jsonify({
        'message': 'Token is valid',
        'user_id': current_user_id,
        'role': current_user_role
    }), 200


@auth_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user_id, current_user_role):
    """
    Get all users (Admin only)
    """
    try:
        db = get_db()
        User = get_user_model()
        
        users = User.query.all()
        
        return jsonify({
            'message': 'Users retrieved successfully',
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
        }), 200
    
    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({'message': 'Failed to retrieve users', 'error': str(e)}), 500


@auth_bp.route('/user/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user_id, current_user_role, user_id):
    """
    Delete user (Admin only)
    """
    if current_user_id == user_id:
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    try:
        db = get_db()
        User = get_user_model()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': f'User {user.username} deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Delete user error: {str(e)}")
        return jsonify({'message': 'Failed to delete user', 'error': str(e)}), 500
