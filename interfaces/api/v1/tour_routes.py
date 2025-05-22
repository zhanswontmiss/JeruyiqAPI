from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from interfaces.api.v1 import create_blueprint
from core.tour.services.tour_service import TourService
from core.common.utils import paginate

bp = create_blueprint('tour')
tour_service = TourService()

@bp.route('/tours', methods=['GET'])
def get_tours():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'destination': request.args.get('destination'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'duration': request.args.get('duration', type=int),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'difficulty': request.args.get('difficulty'),
        'category': request.args.get('category')
    }
    
    filters = {k: v for k, v in filters.items() if v is not None}
    
    tours = tour_service.get_tours(filters)
    paginated = paginate(tours, page, per_page)
    
    return jsonify({
        'items': [tour.to_dict() for tour in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/tours/<tour_id>', methods=['GET'])
def get_tour(tour_id):
    tour = tour_service.get_tour(tour_id)
    
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    return jsonify(tour.to_dict())

@bp.route('/tours/<tour_id>/book', methods=['POST'])
@jwt_required()
def book_tour(tour_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['start_date', 'participants']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        booking = tour_service.book_tour(
            tour_id=tour_id,
            user_id=user_id,
            start_date=data['start_date'],
            participants=data['participants'],
            special_requirements=data.get('special_requirements')
        )
        
        return jsonify(booking.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/tours/categories', methods=['GET'])
def get_tour_categories():
    categories = tour_service.get_categories()
    return jsonify(categories)

@bp.route('/tours/destinations', methods=['GET'])
def get_tour_destinations():
    destinations = tour_service.get_destinations()
    return jsonify(destinations)

@bp.route('/tours/<tour_id>/reviews', methods=['GET'])
def get_tour_reviews(tour_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = tour_service.get_tour_reviews(tour_id)
    paginated = paginate(reviews, page, per_page)
    
    return jsonify({
        'items': [review.to_dict() for review in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/tours/<tour_id>/reviews', methods=['POST'])
@jwt_required()
def add_tour_review(tour_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['rating', 'comment']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        review = tour_service.add_review(
            tour_id=tour_id,
            user_id=user_id,
            rating=data['rating'],
            comment=data['comment']
        )
        
        return jsonify(review.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
