from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from interfaces.api.v1 import create_blueprint
from core.booking.services.booking_service import BookingService
from core.common.utils import paginate

bp = create_blueprint('booking')
booking_service = BookingService()

@bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required = ['property_id', 'check_in_date', 'check_out_date', 'guests']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Parse dates
        check_in = datetime.fromisoformat(data['check_in_date'])
        check_out = datetime.fromisoformat(data['check_out_date'])
        
        booking = booking_service.create_booking(
            user_id=user_id,
            property_id=data['property_id'],
            check_in_date=check_in,
            check_out_date=check_out,
            guests=data['guests'],
            special_requests=data.get('special_requests')
        )
        
        return jsonify(booking.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    bookings = booking_service.get_user_bookings(user_id)
    paginated = paginate(bookings, page, per_page)
    
    return jsonify({
        'items': [booking.to_dict() for booking in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    booking = booking_service.get_booking(booking_id)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Verify booking belongs to user
    if booking.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    return jsonify(booking.to_dict())

@bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    booking = booking_service.get_booking(booking_id)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    if booking.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    try:
        updated_booking = booking_service.update_booking(
            booking_id=booking_id,
            guests=data.get('guests'),
            special_requests=data.get('special_requests')
        )
        
        return jsonify(updated_booking.to_dict())
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    booking = booking_service.get_booking(booking_id)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    if booking.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    booking_service.cancel_booking(booking_id)
    
    return jsonify({'message': 'Booking cancelled successfully'}), 200
