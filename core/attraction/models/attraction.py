from datetime import datetime
from core.database.postgres.database import db

class Attraction(db.Model):
    """Attraction model."""
    __tablename__ = 'attractions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(500))
    price = db.Column(db.Float)
    opening_hours = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Attraction {self.name}>'
    
    def to_dict(self):
        """Convert attraction object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'price': self.price,
            'opening_hours': self.opening_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
