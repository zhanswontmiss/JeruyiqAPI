from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def init_db(app):
    """Initialize the database with the application"""
    db.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they're registered
        from core.database.postgres.models import User, Property, Booking
        from core.guide.models.guide import Guide
        from core.tour.models.tour import Tour
