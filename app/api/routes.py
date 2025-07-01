from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Paste
from app.api.auth import token_required, admin_required
import base64

api_bp = Blueprint('api', __name__)

# Auth endpoints
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        # Generate simple token (in production, use proper JWT)
        token = base64.b64encode(f"{user.username}:{request.app.config['SECRET_KEY']}".encode()).decode()
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """API registration endpoint"""
    data = request.get_json()
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

# Paste endpoints
@api_bp.route('/pastes', methods=['GET'])
def get_pastes():
    """Get all public pastes"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    pastes = Paste.query.filter_by(is_public=True).order_by(
        Paste.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'pastes': [paste.to_dict() for paste in pastes.items],
        'total': pastes.total,
        'pages': pastes.pages,
        'current_page': page,
        'per_page': per_page
    })

@api_bp.route('/pastes', methods=['POST'])
def create_paste():
    """Create a new paste"""
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    # Optional authentication
    user_id = None
    if hasattr(request, 'current_user'):
        user_id = request.current_user.id
    
    paste = Paste(
        title=data.get('title', 'Untitled'),
        content=data['content'],
        language=data.get('language', 'text'),
        is_public=data.get('is_public', True),
        user_id=user_id
    )
    
    db.session.add(paste)
    db.session.commit()
    
    return jsonify(paste.to_dict()), 201

@api_bp.route('/pastes/<unique_id>', methods=['GET'])
def get_paste(unique_id):
    """Get a specific paste"""
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if user can view this paste
    if not paste.is_public:
        if not hasattr(request, 'current_user') or (
            request.current_user.id != paste.user_id and not request.current_user.is_superuser
        ):
            return jsonify({'error': 'This paste is private'}), 403
    
    paste.increment_views()
    return jsonify(paste.to_dict())

@api_bp.route('/pastes/<unique_id>/raw', methods=['GET'])
def get_paste_raw(unique_id):
    """Get raw content of a paste"""
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if user can view this paste
    if not paste.is_public:
        if not hasattr(request, 'current_user') or (
            request.current_user.id != paste.user_id and not request.current_user.is_superuser
        ):
            return jsonify({'error': 'This paste is private'}), 403
    
    return paste.content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@api_bp.route('/pastes/<unique_id>', methods=['PUT'])
@token_required
def update_paste(unique_id):
    """Update a paste"""
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if user can edit this paste
    if request.current_user.id != paste.user_id and not request.current_user.is_superuser:
        return jsonify({'error': 'You can only edit your own pastes'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'title' in data:
        paste.title = data['title']
    if 'content' in data:
        paste.content = data['content']
    if 'language' in data:
        paste.language = data['language']
    if 'is_public' in data:
        paste.is_public = data['is_public']
    
    db.session.commit()
    return jsonify(paste.to_dict())

@api_bp.route('/pastes/<unique_id>', methods=['DELETE'])
@token_required
def delete_paste(unique_id):
    """Delete a paste"""
    paste = Paste.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if user can delete this paste
    if request.current_user.id != paste.user_id and not request.current_user.is_superuser:
        return jsonify({'error': 'You can only delete your own pastes'}), 403
    
    db.session.delete(paste)
    db.session.commit()
    return jsonify({'message': 'Paste deleted successfully'})

# User endpoints
@api_bp.route('/users/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    return jsonify(request.current_user.to_dict())

@api_bp.route('/users/me/pastes', methods=['GET'])
@token_required
def get_user_pastes():
    """Get current user's pastes"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    pastes = request.current_user.pastes.order_by(
        Paste.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'pastes': [paste.to_dict() for paste in pastes.items],
        'total': pastes.total,
        'pages': pastes.pages,
        'current_page': page,
        'per_page': per_page
    })

@api_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users():
    """Get all users (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page,
        'per_page': per_page
    })

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.is_superuser and request.current_user.id != user.id:
        return jsonify({'error': 'Cannot delete other superusers'}), 403
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}) 