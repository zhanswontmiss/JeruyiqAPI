from flask import Flask, request, jsonify
import jwt
import datetime
import os
from sqlalchemy import Column, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///auth.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def generate_token(user_id, email, role):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'email': email,
        'role': role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'message': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'message': 'Invalid token'}

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "auth-service"})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    db = get_db()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = User(
        email=email,
        password_hash=hashed_password,
        role=data.get('role', 'user')
    )
    
    db.add(new_user)
    db.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': new_user.user_id
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    db = get_db()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate token
    token = generate_token(user.user_id, user.email, user.role)
    
    return jsonify({
        'token': token,
        'user_id': user.user_id,
        'email': user.email,
        'role': user.role
    }), 200

@app.route('/auth/validate-token', methods=['POST'])
def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    decoded = decode_token(token)
    
    if 'message' in decoded:
        return jsonify({'message': decoded['message']}), 401
    
    return jsonify(decoded), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)