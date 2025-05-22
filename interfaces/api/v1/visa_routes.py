from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from interfaces.api.v1 import create_blueprint
from core.visa.services.visa_service import VisaService
from core.common.utils import paginate

bp = create_blueprint('visa')
visa_service = VisaService()

@bp.route('/visa/requirements', methods=['GET'])
def get_visa_requirements():
    origin_country = request.args.get('origin')
    destination_country = request.args.get('destination')
    
    if not origin_country or not destination_country:
        return jsonify({'error': 'Origin and destination countries are required'}), 400
    
    requirements = visa_service.get_visa_requirements(
        origin_country=origin_country,
        destination_country=destination_country
    )
    
    return jsonify(requirements)

@bp.route('/visa/check-eligibility', methods=['POST'])
def check_visa_eligibility():
    data = request.get_json()
    
    required = ['nationality', 'destination_country', 'stay_duration', 'visit_purpose']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        eligibility = visa_service.check_eligibility(
            nationality=data['nationality'],
            destination_country=data['destination_country'],
            stay_duration=data['stay_duration'],
            visit_purpose=data['visit_purpose'],
            additional_info=data.get('additional_info', {})
        )
        
        return jsonify(eligibility)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/visa/apply', methods=['POST'])
@jwt_required()
def apply_for_visa():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['destination_country', 'visit_purpose', 'planned_arrival_date', 'planned_departure_date']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        application = visa_service.create_visa_application(
            user_id=user_id,
            destination_country=data['destination_country'],
            visit_purpose=data['visit_purpose'],
            planned_arrival_date=data['planned_arrival_date'],
            planned_departure_date=data['planned_departure_date'],
            additional_info=data.get('additional_info', {})
        )
        
        return jsonify(application.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/visa/applications', methods=['GET'])
@jwt_required()
def get_user_applications():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    applications = visa_service.get_user_applications(user_id)
    paginated = paginate(applications, page, per_page)
    
    return jsonify({
        'items': [app.to_dict() for app in paginated['items']],
        'total': paginated['total'],
        'page': paginated['page'],
        'per_page': paginated['per_page'],
        'total_pages': paginated['total_pages']
    })

@bp.route('/visa/applications/<application_id>', methods=['GET'])
@jwt_required()
def get_application_status(application_id):
    user_id = get_jwt_identity()
    
    application = visa_service.get_application(application_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    if application.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    return jsonify(application.to_dict())

@bp.route('/visa/countries', methods=['GET'])
def get_supported_countries():
    countries = visa_service.get_supported_countries()
    return jsonify(countries)

@bp.route('/visa/purposes', methods=['GET'])
def get_visa_purposes():
    purposes = visa_service.get_visa_purposes()
    return jsonify(purposes)
