from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from interfaces.api.v1 import create_blueprint
from core.guide.services.guide_service import GuideService
from core.common.utils import paginate

bp = create_blueprint('guide')
guide_service = GuideService()

@bp.route('/guides', methods=['GET'])
def get_guides():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'location': request.args.get('location'),
        'languages': request.args.getlist('languages'),
        'specialties': request.args.getlist('specialties'),
        'min_rating': request.args.get('min_rating', type=float),
        'availability_date': request.args.get('availability_date')
    }
    
    filters = {k: v for k, v in filters.items() if v is not None}
    
    guides = guide_service.get_guides(filters)
    paginated = paginate(guides, page, per_page)
    
    return jsonify({
        'items': [guide.to_dict() for guide in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/guides/<guide_id>', methods=['GET'])
def get_guide(guide_id):
    guide = guide_service.get_guide(guide_id)
    
    if not guide:
        return jsonify({'error': 'Guide not found'}), 404
    
    return jsonify(guide.to_dict())

@bp.route('/guides/<guide_id>/availability', methods=['GET'])
def check_guide_availability(guide_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    try:
        availability = guide_service.check_availability(guide_id, start_date, end_date)
        return jsonify(availability)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/guides/<guide_id>/book', methods=['POST'])
@jwt_required()
def book_guide(guide_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['start_date', 'end_date', 'tour_details']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        booking = guide_service.book_guide(
            guide_id=guide_id,
            user_id=user_id,
            start_date=data['start_date'],
            end_date=data['end_date'],
            tour_details=data['tour_details'],
            special_requirements=data.get('special_requirements')
        )
        
        return jsonify(booking.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/guides/<guide_id>/reviews', methods=['GET'])
def get_guide_reviews(guide_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = guide_service.get_guide_reviews(guide_id)
    paginated = paginate(reviews, page, per_page)
    
    return jsonify({
        'items': [review.to_dict() for review in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/guides/<guide_id>/reviews', methods=['POST'])
@jwt_required()
def add_guide_review(guide_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['rating', 'comment']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        review = guide_service.add_review(
            guide_id=guide_id,
            user_id=user_id,
            rating=data['rating'],
            comment=data['comment']
        )
        
        return jsonify(review.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/guides/specialties', methods=['GET'])
def get_specialties():
    specialties = guide_service.get_specialties()
    return jsonify(specialties)

@bp.route('/guides/languages', methods=['GET'])
def get_languages():
    languages = guide_service.get_languages()
    return jsonify(languages)
