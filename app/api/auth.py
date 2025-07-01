from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user
from app.models import User
import base64

def token_required(f):
    """Decorator to require API token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                elif auth_header.startswith('Basic '):
                    # Basic auth: base64(username:password)
                    credentials = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
                    username, password = credentials.split(':', 1)
                    user = User.query.filter_by(username=username).first()
                    if user and user.check_password(password):
                        request.current_user = user
                        return f(*args, **kwargs)
            except:
                pass
        
        # Check for token in query params
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # For now, we'll use a simple token system
        # In production, you'd want to use proper JWT tokens
        try:
            # Simple token format: base64(username:secret)
            decoded = base64.b64decode(token).decode('utf-8')
            username, secret = decoded.split(':', 1)
            user = User.query.filter_by(username=username).first()
            if user and secret == current_app.config['SECRET_KEY']:
                request.current_user = user
                return f(*args, **kwargs)
        except:
            pass
        
        return jsonify({'error': 'Token is invalid'}), 401
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user.is_superuser:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function 