from flask import Flask, request, jsonify
import os
import uuid
from functools import wraps
import requests
import logging
from dotenv import load_dotenv

# Import the Gemini AI model functionality
from gemini_ai_model import get_response, ChatSessionManager

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

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
        except requests.RequestException as e:
            logger.error(f"Error communicating with auth service: {e}")
            return jsonify({'message': 'Auth service unavailable'}), 503
            
    return decorated

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "ai-service"})

# Chat endpoint
@app.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    user_id = current_user.get('sub')  # Get user ID from token
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    if not session_id:
        # Generate a session ID if not provided
        session_id = f"{user_id}_{str(uuid.uuid4())}"
    
    try:
        # Use the user ID as part of the session ID for better tracking
        full_session_id = f"{user_id}_{session_id}"
        ai_response = get_response(user_message, full_session_id)
        
        return jsonify({
            "response": ai_response,
            "session_id": session_id
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return jsonify({"error": "Failed to process request"}), 500

# Get available sessions for a user
@app.route('/sessions', methods=['GET'])
@token_required
def get_sessions(current_user):
    user_id = current_user.get('sub')
    
    # This would require modifying the ChatSessionManager to track sessions by user
    # For now, we'll return a placeholder
    return jsonify({
        "message": "Session retrieval not implemented yet",
        "user_id": user_id
    }), 501

# Clear chat session endpoint
@app.route('/sessions/<session_id>', methods=['DELETE'])
@token_required
def clear_session(current_user, session_id):
    user_id = current_user.get('sub')
    
    # Add user ID to session ID for security (prevents users from clearing others' sessions)
    full_session_id = f"{user_id}_{session_id}"
    
    try:
        ChatSessionManager.clear_session(full_session_id)
        return jsonify({"message": "Session cleared successfully"}), 200
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        return jsonify({"error": "Failed to clear session"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)