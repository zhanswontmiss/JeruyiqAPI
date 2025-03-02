from flask import Flask, request, jsonify, Response
import requests
import os
from functools import wraps
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs from environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5002")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:5003")

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "api-gateway"})

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
                
            # Add user info to request context for downstream services
            return f(response.json(), *args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Error communicating with auth service: {e}")
            return jsonify({'message': 'Service unavailable'}), 503
            
    return decorated

# Routes for Auth Service
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=request.json)
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with auth service: {e}")
        return jsonify({'message': 'Auth service unavailable'}), 503

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=request.json)
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with auth service: {e}")
        return jsonify({'message': 'Auth service unavailable'}), 503

# Routes for User Service
@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        response = requests.get(
            f"{USER_SERVICE_URL}/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with user service: {e}")
        return jsonify({'message': 'User service unavailable'}), 503

@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        response = requests.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with user service: {e}")
        return jsonify({'message': 'User service unavailable'}), 503

# Routes for AI Service
@app.route('/ai/chat', methods=['POST'])
@token_required
def chat(current_user):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        
        # Forward the request to the AI service
        data = request.json
        data['user_id'] = current_user.get('sub')  # Add user ID from JWT token
        
        response = requests.post(
            f"{AI_SERVICE_URL}/chat",
            json=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with AI service: {e}")
        return jsonify({'message': 'AI service unavailable'}), 503

@app.route('/ai/sessions/<session_id>', methods=['DELETE'])
@token_required
def clear_chat_session(current_user, session_id):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        response = requests.delete(
            f"{AI_SERVICE_URL}/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return Response(response.content, response.status_code, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        logger.error(f"Error communicating with AI service: {e}")
        return jsonify({'message': 'AI service unavailable'}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)