from flask import Flask, request, jsonify
import requests
import os
from sqlalchemy import Column, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from functools import wraps
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///users.db")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model
class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Permission constants
class Permission:
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE_USERS = "manage_users"
    
    ROLE_PERMISSIONS = {
        "user": {READ},
        "guider": {READ, WRITE},
        "admin": {READ, WRITE, DELETE, MANAGE_USERS},
    }

    @staticmethod
    def has_permission(role, permission):
        return permission in Permission.ROLE_PERMISSIONS.get(role, set())

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Validate token with auth service
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/auth/validate-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                return jsonify({'message': 'Token is invalid'}), 401
                
            # Add user info to request context
            return f(response.json(), *args, **kwargs)
        except requests.RequestException:
            return jsonify({'message': 'Auth service unavailable'}), 503
            
    return decorated

# Permission middleware
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            role = current_user.get('role', 'user')
            if not Permission.has_permission(role, permission):
                return jsonify({'message': 'Permission denied'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user-service"})

@app.route('/user-profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    
    db = get_db()
    
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == data.get('user_id')).first()
    if existing_profile:
        return jsonify({'message': 'Profile already exists'}), 409
    
    # Create profile
    new_profile = UserProfile(
        user_id=data.get('user_id'),
        name=data.get('name'),
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        role=data.get('role', 'user')
    )
    
    db.add(new_profile)
    db.commit()
    
    return jsonify({
        'message': 'Profile created successfully',
        'user_id': new_profile.user_id
    }), 201

@app.route('/users', methods=['GET'])
@token_required
@require_permission(Permission.MANAGE_USERS)
def get_all_users(current_user):
    db = get_db()
    users = db.query(UserProfile).all()
    
    result = []
    for user in users:
        result.append({
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role
        })
    
    return jsonify(result), 200

@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    # Check if user is requesting their own profile or has manage_users permission
    if user_id != current_user.get('sub') and not Permission.has_permission(current_user.get('role'), Permission.MANAGE_USERS):
        return jsonify({'message': 'Permission denied'}), 403
    
    db = get_db()
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'phone_number': user.phone_number,
        'role': user.role
    }), 200

@app.route('/users/<user_id>/role', methods=['PUT'])
@token_required
@require_permission(Permission.MANAGE_USERS)
def update_role(current_user, user_id):
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role:
        return jsonify({'message': 'Role is required'}), 400
    
    db = get_db()
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.role = new_role
    db.commit()
    
    return jsonify({
        'message': 'Role updated successfully',
        'user_id': user.user_id,
        'role': user.role
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)