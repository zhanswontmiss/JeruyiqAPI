from functools import wraps
from flask import request, g, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def jwt_or_login_required(f):
    """Decorator to check if user is authenticated via JWT token or login session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First try to verify JWT token in header
        try:
            verify_jwt_in_request()
            g.user_id = get_jwt_identity()
            return f(*args, **kwargs)
        except:
            # If no valid JWT token, check session
            if 'jwt_token' not in session:
                return {'error': 'Authentication required'}, 401
            try:
                # Try to use token from session
                request.headers['Authorization'] = f'Bearer {session["jwt_token"]}'
                verify_jwt_in_request()
                g.user_id = get_jwt_identity()
                return f(*args, **kwargs)
            except:
                session.pop('jwt_token', None)
                return {'error': 'Invalid or expired token'}, 401
    return decorated_function
