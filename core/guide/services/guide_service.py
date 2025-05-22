from datetime import datetime
from core.database.postgres.database import db
from core.common.exceptions import ResourceNotFoundError, ValidationError
from core.guide.models.guide import Guide

class Guide:
    """Guide model - You may want to move this to core/guide/models/guide.py"""
    __tablename__ = 'guides'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    biography = db.Column(db.Text)
    specialties = db.Column(db.String(500))
    languages = db.Column(db.String(200))
    rate_per_day = db.Column(db.Float)
    years_experience = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GuideService:
    def create_guide(self, user_id: int, data: dict) -> Guide:
        """Create a new guide profile."""
        guide = Guide(
            user_id=user_id,
            biography=data.get('biography', ''),
            specialties=data.get('specialties', ''),
            languages=data.get('languages', ''),
            rate_per_day=data.get('rate_per_day'),
            years_experience=data.get('years_experience', 0)
        )

        db.session.add(guide)
        db.session.commit()

        return guide

    def get_guide(self, guide_id: int) -> Guide:
        """Get a guide by ID."""
        guide = Guide.query.get(guide_id)
        if not guide:
            raise ResourceNotFoundError("Guide", str(guide_id))
        return guide

    def get_guides(self, page: int = 1, per_page: int = 10, filters: dict = None):
        """Get all guides with optional filtering."""
        query = Guide.query

        if filters:
            if 'min_rate' in filters:
                query = query.filter(Guide.rate_per_day >= filters['min_rate'])
            if 'max_rate' in filters:
                query = query.filter(Guide.rate_per_day <= filters['max_rate'])
            if 'min_experience' in filters:
                query = query.filter(Guide.years_experience >= filters['min_experience'])
            if 'languages' in filters:
                query = query.filter(Guide.languages.ilike(f"%{filters['languages']}%"))

        return query.paginate(page=page, per_page=per_page)

    def update_guide(self, guide_id: int, data: dict) -> Guide:
        """Update a guide's profile."""
        guide = self.get_guide(guide_id)

        for field in ['biography', 'specialties', 'languages', 'rate_per_day', 'years_experience']:
            if field in data:
                setattr(guide, field, data[field])

        db.session.commit()
        return guide

    def delete_guide(self, guide_id: int):
        """Delete a guide's profile."""
        guide = self.get_guide(guide_id)
        db.session.delete(guide)
        db.session.commit()
