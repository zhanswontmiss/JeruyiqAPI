from core.database.postgres.database import db
from datetime import datetime

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(500))
    price_per_night = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='property', lazy=True)
    owner = db.relationship('User', backref='properties', lazy=True)

    def __repr__(self):
        return f'<Property {self.name}>'
