from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

from flask import current_app, request
from flask_jwt_extended import create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from core.common.exceptions import AuthenticationError, AuthorizationError

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return generate_password_hash(password)

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return check_password_hash(stored_password, provided_password)

def create_token(user_id: str, additional_claims: Dict[str, Any] = None) -> str:
    """Create a new access token."""
    claims = {'sub': str(user_id)}
    if additional_claims:
        claims.update(additional_claims)
    
    expires_delta = timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    access_token = create_access_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=expires_delta
    )
    return access_token

def requires_roles(*roles):
    """Decorator to check if user has required roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            if not current_user:
                raise AuthenticationError()
            
            user_roles = current_user.get('roles', [])
            if not any(role in user_roles for role in roles):
                raise AuthorizationError("Insufficient permissions")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
