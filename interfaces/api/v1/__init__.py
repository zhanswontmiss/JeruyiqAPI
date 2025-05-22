from flask import Blueprint, jsonify
from core.common.exceptions import JeruyiqException

def create_blueprint(name: str) -> Blueprint:
    """Create a blueprint with common error handlers."""
    bp = Blueprint(name, __name__)

    @bp.errorhandler(JeruyiqException)
    def handle_jeruyiq_error(error):
        response = {
            'error': error.__class__.__name__,
            'message': error.message
        }
        if hasattr(error, 'errors'):
            response['errors'] = error.errors
        return jsonify(response), error.status_code

    @bp.errorhandler(Exception)
    def handle_error(error):
        return jsonify({
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred'
        }), 500

    return bp