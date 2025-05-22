from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from interfaces.api.v1 import create_blueprint
from core.property.services.property_service import PropertyService
from core.common.utils import paginate

bp = create_blueprint('property')
property_service = PropertyService()

@bp.route('/properties', methods=['GET'])
def get_properties():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    filters = {
        'location': request.args.get('location'),
        'check_in': request.args.get('check_in'),
        'check_out': request.args.get('check_out'),
        'guests': request.args.get('guests', type=int),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'amenities': request.args.getlist('amenities'),
        'property_type': request.args.get('property_type')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    properties = property_service.get_properties(filters)
    paginated = paginate(properties, page, per_page)
    
    return jsonify({
        'items': [prop.to_dict() for prop in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    property = property_service.get_property(property_id)
    
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    return jsonify(property.to_dict())

@bp.route('/properties/<int:property_id>/availability', methods=['GET'])
def check_availability(property_id):
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    
    if not check_in or not check_out:
        return jsonify({'error': 'Check-in and check-out dates are required'}), 400
    
    try:
        availability = property_service.check_availability(
            property_id,
            check_in,
            check_out
        )
        
        return jsonify(availability)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/properties/search', methods=['GET'])
def search_properties():
    query = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    properties = property_service.search_properties(query)
    paginated = paginate(properties, page, per_page)
    
    return jsonify({
        'items': [prop.to_dict() for prop in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/properties/featured', methods=['GET'])
def get_featured_properties():
    limit = request.args.get('limit', 6, type=int)
    properties = property_service.get_featured_properties(limit)
    
    return jsonify([prop.to_dict() for prop in properties])
