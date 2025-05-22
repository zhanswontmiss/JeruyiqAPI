from core.common.exceptions import ResourceNotFoundError, ValidationError
from core.tour.models.tour import Tour
from core.database.postgres.database import db

class TourService:
    def create_tour(self, data: dict) -> Tour:
        """Create a new tour."""
        tour = Tour(
            name=data['name'],
            description=data.get('description', ''),
            duration_days=data['duration_days'],
            price=data['price'],
            max_participants=data.get('max_participants'),
            guide_id=data.get('guide_id')
        )

        db.session.add(tour)
        db.session.commit()

        return tour

    def get_tour(self, tour_id: int) -> Tour:
        """Get a tour by ID."""
        tour = Tour.query.get(tour_id)
        if not tour:
            raise ResourceNotFoundError("Tour", str(tour_id))
        return tour

    def get_tours(self, page: int = 1, per_page: int = 10, filters: dict = None):
        """Get all tours with optional filtering."""
        query = Tour.query

        if filters:
            if 'min_price' in filters:
                query = query.filter(Tour.price >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(Tour.price <= filters['max_price'])
            if 'guide_id' in filters:
                query = query.filter(Tour.guide_id == filters['guide_id'])
            if 'duration_days' in filters:
                query = query.filter(Tour.duration_days <= filters['duration_days'])

        return query.paginate(page=page, per_page=per_page)

    def update_tour(self, tour_id: int, data: dict) -> Tour:
        """Update a tour."""
        tour = self.get_tour(tour_id)

        for field in ['name', 'description', 'duration_days', 'price', 'max_participants', 'guide_id']:
            if field in data:
                setattr(tour, field, data[field])

        db.session.commit()
        return tour

    def delete_tour(self, tour_id: int):
        """Delete a tour."""
        tour = self.get_tour(tour_id)
        db.session.delete(tour)
        db.session.commit()
