from core.database.postgres.database import db
from core.common.exceptions import ResourceNotFoundError, ValidationError
from core.attraction.models.attraction import Attraction

class AttractionService:
    def create_attraction(self, data: dict) -> Attraction:
        """Create a new attraction."""
        attraction = Attraction(
            name=data['name'],
            description=data.get('description', ''),
            location=data['location'],
            price=data.get('price'),
            opening_hours=data.get('opening_hours')
        )

        db.session.add(attraction)
        db.session.commit()

        return attraction

    def get_attraction(self, attraction_id: int) -> Attraction:
        """Get an attraction by ID."""
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            raise ResourceNotFoundError("Attraction", str(attraction_id))
        return attraction

    def get_attractions(self, page: int = 1, per_page: int = 10, filters: dict = None):
        """Get all attractions with optional filtering."""
        query = Attraction.query

        if filters:
            if 'location' in filters:
                query = query.filter(Attraction.location.ilike(f"%{filters['location']}%"))
            if 'min_price' in filters:
                query = query.filter(Attraction.price >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(Attraction.price <= filters['max_price'])

        return query.paginate(page=page, per_page=per_page)

    def update_attraction(self, attraction_id: int, data: dict) -> Attraction:
        """Update an attraction."""
        attraction = self.get_attraction(attraction_id)

        for field in ['name', 'description', 'location', 'price', 'opening_hours']:
            if field in data:
                setattr(attraction, field, data[field])

        db.session.commit()
        return attraction

    def delete_attraction(self, attraction_id: int):
        """Delete an attraction."""
        attraction = self.get_attraction(attraction_id)
        db.session.delete(attraction)
        db.session.commit()
