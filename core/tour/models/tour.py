from datetime import datetime
from core.database.postgres.database import db

class Tour(db.Model):
    """Tour model."""
    __tablename__ = 'tours'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_participants = db.Column(db.Integer)
    guide_id = db.Column(db.Integer, db.ForeignKey('guides.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guide = db.relationship('Guide', backref='tours', lazy=True)

    def __repr__(self):
        return f'<Tour {self.name}>'
    
    def to_dict(self):
        """Convert tour object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_days': self.duration_days,
            'price': self.price,
            'max_participants': self.max_participants,
            'guide_id': self.guide_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
