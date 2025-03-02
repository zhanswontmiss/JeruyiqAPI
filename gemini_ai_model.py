import google.generativeai as genai
import os
import redis
import json
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables
api_key = os.getenv("GEMINI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class ChatSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, List[str]]] = self._load_history()
        self.model = self._initialize_model()
        self.chat = self.model.start_chat(history=self.history)
    
    def _load_history(self) -> List[Dict[str, List[str]]]:
        """Load conversation history from Redis."""
        try:
            history_data = redis_client.get(f"chat_history:{self.session_id}")
            if history_data:
                return json.loads(history_data)
            return []
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []
    
    def _save_history(self):
        """Save conversation history to Redis."""
        try:
            redis_client.set(
                f"chat_history:{self.session_id}", 
                json.dumps(self.history),
                ex=86400  # Expire after 24 hours
            )
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    @staticmethod
    def _initialize_model():
        """Initialize the Gemini model with configuration."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "response_mime_type": "text/plain",
        }
        
        return genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config
        )
    
    def send_message(self, message: str) -> str:
        """Send a message and get response from the model."""
        if not message.strip():
            raise ValueError("Message cannot be empty")
        
        try:
            # Add user message to history
            self.history.append({"role": "user", "parts": [message]})
            
            # Get response from model
            response = self.chat.send_message(message)
            model_response = response.text.strip()
            
            # Add model response to history
            self.history.append({"role": "model", "parts": [model_response]})
            
            # Save updated history
            self._save_history()
            
            return model_response
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def clear_history(self):
        """Clear the conversation history."""
        self.history = []
        redis_client.delete(f"chat_history:{self.session_id}")
        self.chat = self.model.start_chat(history=self.history)

class ChatSessionManager:
    _instances: Dict[str, ChatSession] = {}
    
    @classmethod
    def get_session(cls, session_id: str) -> ChatSession:
        """Get or create a chat session for the given session ID."""
        if session_id not in cls._instances:
            cls._instances[session_id] = ChatSession(session_id)
        return cls._instances[session_id]
    
    @classmethod
    def clear_session(cls, session_id: str):
        """Clear a specific chat session."""
        if session_id in cls._instances:
            session = cls._instances[session_id]
            session.clear_history()
            del cls._instances[session_id]
    
    @classmethod
    def clear_all_sessions(cls):
        """Clear all chat sessions."""
        for session_id, session in cls._instances.items():
            session.clear_history()
        cls._instances.clear()

def get_response(user_message: str, session_id: str) -> str:
    """
    Get a response from Gemini AI based on the user's input.
    
    Args:
        user_message: The message from the user
        session_id: Session identifier for maintaining conversation context
    
    Returns:
        The model's response
    
    Raises:
        ValueError: If the message is empty or session management fails
        Exception: For other errors during processing
    """
    if not session_id:
        raise ValueError("No session ID provided")
    
    if not user_message.strip():
        raise ValueError("Message cannot be empty")
    
    try:
        chat_session = ChatSessionManager.get_session(session_id)
        return chat_session.send_message(user_message)
    except Exception as e:
        logger.error(f"Failed to get response: {e}")
        raise