"""
users.py - User management API endpoints
CRUD operations: Create, Read, Update, Delete users
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import models
from utils.validation import validate_username, validate_password

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# ============ DECORATORS ============

def get_user_model():
    """Get User model from models module"""
    return models.User

def get_db():
    """Get db instance from models module"""
    return models.db

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        User = get_user_model()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============ CREATE USER (POST) ============

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """
    Create new user (admin only)
    
    Request body:
    {
        "username": "string",
        "password": "string",
        "email": "string (optional)",
        "full_name": "string (optional)",
        "role": "user|admin (default: user)"
    }
    """
    try:
        User = get_user_model()
        db = get_db()
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is empty'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        role = data.get('role', 'user')
        
        # Validate username
        if not validate_username(username):
            return jsonify({
                'success': False,
                'message': 'Username must be 3-20 characters, alphanumeric and underscore only'
            }), 400
        
        # Check username exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 409
        
        # Validate password
        if not validate_password(password):
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        # Validate role
        if role not in ['user', 'admin']:
            role = 'user'
        
        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            full_name=full_name,
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name,
                'role': new_user.role,
                'is_active': new_user.is_active,
                'created_at': new_user.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating user: {str(e)}'
        }), 500

# ============ READ USERS (GET) ============

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users (authenticated users only)
    Query params:
    - role: filter by role (user/admin)
    - is_active: filter by active status (true/false)
    """
    try:
        User = get_user_model()
        db = get_db()
        
        # Get filters from query params
        role = request.args.get('role', None)
        is_active = request.args.get('is_active', None)
        
        query = User.query
        
        # Apply filters
        if role and role in ['user', 'admin']:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        users = query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            } for user in users]
        }), 200
        
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }), 500

# ============ READ SINGLE USER (GET) ============

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get single user by ID"""
    try:
        User = get_user_model()
        db = get_db()
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching user: {str(e)}'
        }), 500

# ============ UPDATE USER (PUT) ============

@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update user (admin only)
    
    Request body:
    {
        "email": "string (optional)",
        "full_name": "string (optional)",
        "password": "string (optional)",
        "is_active": boolean (optional),
        "role": "user|admin (optional)"
    }
    """
    try:
        User = get_user_model()
        db = get_db()
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is empty'
            }), 400
        
        # Update fields
        if 'email' in data:
            user.email = data['email'].strip()
        
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'password' in data and data['password']:
            password = data['password']
            if not validate_password(password):
                return jsonify({
                    'success': False,
                    'message': 'Password must be at least 6 characters'
                }), 400
            user.password_hash = generate_password_hash(password)
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'role' in data and data['role'] in ['user', 'admin']:
            user.role = data['role']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }), 500

# ============ DELETE USER (DELETE) ============

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        User = get_user_model()
        db = get_db()
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Prevent deleting the last admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete the last admin user'
                }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }), 500

# ============ DEACTIVATE USER (POST) ============

@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user instead of deleting"""
    try:
        User = get_user_model()
        db = get_db()
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deactivating user: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error deactivating user: {str(e)}'
        }), 500
