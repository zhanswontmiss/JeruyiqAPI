class JeruyiqException(Exception):
    """Base exception for all Jeruyiq-specific exceptions."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AuthenticationError(JeruyiqException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(JeruyiqException):
    """Raised when user doesn't have permission."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class ResourceNotFoundError(JeruyiqException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, status_code=404)

class ValidationError(JeruyiqException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed", errors: dict = None):
        super().__init__(message, status_code=400)
        self.errors = errors or {}
