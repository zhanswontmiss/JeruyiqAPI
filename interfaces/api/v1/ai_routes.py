import os
from flask import jsonify, request, session
from interfaces.api.v1 import create_blueprint
from core.ai.gemini_ai_model import ChatSession
import logging

bp = create_blueprint('ai')
logger = logging.getLogger(__name__)

def initialize_ai():
    """Check if the environment is properly configured for AI"""
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize AI on module import
try:
    initialize_ai()
except Exception as e:
    logger.error(f"Failed to initialize AI module: {str(e)}")

@bp.route('/chat/send', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create session ID from user's session
        session_id = session.get('chat_session_id')
        if not session_id:
            session_id = str(hash(request.remote_addr))  # Simple session ID generation
            session['chat_session_id'] = session_id

        # Get or create chat session
        chat_session = ChatSession(session_id)
        
        # Send message and get response
        response = chat_session.send_message(data['message'])
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
