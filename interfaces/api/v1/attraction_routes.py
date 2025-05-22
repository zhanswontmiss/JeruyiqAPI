from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from interfaces.api.v1 import create_blueprint
from core.attraction.services.attraction_service import AttractionService
from core.common.utils import paginate

bp = create_blueprint('attraction')
attraction_service = AttractionService()

@bp.route('/attractions', methods=['GET'])
def get_attractions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'location': request.args.get('location'),
        'category': request.args.get('category'),
        'min_rating': request.args.get('min_rating', type=float),
        'price_range': request.args.get('price_range'),
        'open_now': request.args.get('open_now', type=bool)
    }
    
    filters = {k: v for k, v in filters.items() if v is not None}
    
    attractions = attraction_service.get_attractions(filters)
    paginated = paginate(attractions, page, per_page)
    
    return jsonify({
        'items': [attraction.to_dict() for attraction in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/attractions/<attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    attraction = attraction_service.get_attraction(attraction_id)
    
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404
    
    return jsonify(attraction.to_dict())

@bp.route('/attractions/nearby', methods=['GET'])
def get_nearby_attractions():
    latitude = request.args.get('lat', type=float)
    longitude = request.args.get('lng', type=float)
    radius = request.args.get('radius', 5000, type=int)  # Default 5km radius
    
    if latitude is None or longitude is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    attractions = attraction_service.get_nearby_attractions(latitude, longitude, radius)
    return jsonify([attraction.to_dict() for attraction in attractions])

@bp.route('/attractions/categories', methods=['GET'])
def get_categories():
    categories = attraction_service.get_categories()
    return jsonify(categories)

@bp.route('/attractions/<attraction_id>/reviews', methods=['GET'])
def get_attraction_reviews(attraction_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = attraction_service.get_attraction_reviews(attraction_id)
    paginated = paginate(reviews, page, per_page)
    
    return jsonify({
        'items': [review.to_dict() for review in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/attractions/<attraction_id>/reviews', methods=['POST'])
@jwt_required()
def add_attraction_review(attraction_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['rating', 'comment']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        review = attraction_service.add_review(
            attraction_id=attraction_id,
            user_id=user_id,
            rating=data['rating'],
            comment=data['comment'],
            visit_date=data.get('visit_date')
        )
        
        return jsonify(review.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/attractions/recommended', methods=['GET'])
@jwt_required()
def get_recommended_attractions():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 6, type=int)
    
    attractions = attraction_service.get_recommended_attractions(user_id, limit)
    return jsonify([attraction.to_dict() for attraction in attractions])
