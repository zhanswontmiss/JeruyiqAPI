from datetime import datetime
from core.database.postgres.database import db
from core.common.exceptions import ResourceNotFoundError, ValidationError

class VisaApplication:
    """Visa Application model - You may want to move this to core/visa/models/visa_application.py"""
    __tablename__ = 'visa_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visa_type = db.Column(db.String(50), nullable=False)  # tourist, business, student, etc.
    destination_country = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    decision_date = db.Column(db.DateTime)
    passport_number = db.Column(db.String(50))
    documents = db.Column(db.JSON)  # Store document paths/references
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VisaService:
    def create_application(self, user_id: int, data: dict) -> VisaApplication:
        """Create a new visa application."""
        application = VisaApplication(
            user_id=user_id,
            visa_type=data['visa_type'],
            destination_country=data['destination_country'],
            passport_number=data['passport_number'],
            documents=data.get('documents', {})
        )

        db.session.add(application)
        db.session.commit()

        return application

    def get_application(self, application_id: int) -> VisaApplication:
        """Get a visa application by ID."""
        application = VisaApplication.query.get(application_id)
        if not application:
            raise ResourceNotFoundError("VisaApplication", str(application_id))
        return application

    def get_user_applications(self, user_id: int, page: int = 1, per_page: int = 10):
        """Get all visa applications for a user."""
        return VisaApplication.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page
        )

    def update_application_status(self, application_id: int, status: str, decision_date: datetime = None) -> VisaApplication:
        """Update the status of a visa application."""
        application = self.get_application(application_id)
        
        valid_statuses = ['pending', 'approved', 'rejected', 'processing', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        application.status = status
        if status in ['approved', 'rejected']:
            application.decision_date = decision_date or datetime.utcnow()

        db.session.commit()
        return application

    def get_visa_requirements(self, destination_country: str, visa_type: str = 'tourist') -> dict:
        """Get visa requirements for a specific country and visa type."""
        # This would typically come from a database or external API
        # For now, returning mock data
        return {
            'destination_country': destination_country,
            'visa_type': visa_type,
            'requirements': [
                {
                    'document': 'Valid Passport',
                    'description': 'Must be valid for at least 6 months beyond intended stay'
                },
                {
                    'document': 'Application Form',
                    'description': 'Completed and signed visa application form'
                },
                {
                    'document': 'Photos',
                    'description': 'Recent passport-size photographs'
                },
                {
                    'document': 'Bank Statement',
                    'description': 'Last 3 months bank statements showing sufficient funds'
                }
            ],
            'processing_time': '5-10 business days',
            'fees': {
                'amount': 100,
                'currency': 'USD'
            }
        }
