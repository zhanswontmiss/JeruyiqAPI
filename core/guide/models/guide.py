from datetime import datetime
from core.database.postgres.database import db

class Guide(db.Model):
    """Guide model."""
    __tablename__ = 'guides'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    languages = db.Column(db.JSON)  # List of languages the guide speaks
    specialties = db.Column(db.JSON)  # List of tour types/specialties
    hourly_rate = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='guide', lazy=True, uselist=False)

    def __repr__(self):
        return f'<Guide {self.user.full_name}>'

    def to_dict(self):
        """Convert guide object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'languages': self.languages,
            'specialties': self.specialties,
            'hourly_rate': self.hourly_rate,
            'is_available': self.is_available,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None
        }
