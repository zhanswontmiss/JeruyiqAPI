from core.database.postgres.models import Property, User
from core.database.postgres.database import db
from core.common.exceptions import ResourceNotFoundError, ValidationError

class PropertyService:
    def create_property(self, owner_id: int, data: dict) -> Property:
        """Create a new property listing."""
        # Validate owner exists
        owner = User.query.get(owner_id)
        if not owner:
            raise ResourceNotFoundError("User", str(owner_id))

        property = Property(
            name=data['name'],
            description=data.get('description', ''),
            address=data['address'],
            price_per_night=data['price_per_night'],
            owner_id=owner_id
        )

        db.session.add(property)
        db.session.commit()

        return property

    def get_property(self, property_id: int) -> Property:
        """Get a property by ID."""
        property = Property.query.get(property_id)
        if not property:
            raise ResourceNotFoundError("Property", str(property_id))
        return property

    def get_properties(self, page: int = 1, per_page: int = 10, filters: dict = None):
        """Get all properties with optional filtering."""
        query = Property.query

        if filters:
            if 'min_price' in filters:
                query = query.filter(Property.price_per_night >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(Property.price_per_night <= filters['max_price'])
            if 'owner_id' in filters:
                query = query.filter(Property.owner_id == filters['owner_id'])

        return query.paginate(page=page, per_page=per_page)

    def update_property(self, property_id: int, data: dict) -> Property:
        """Update a property."""
        property = self.get_property(property_id)

        if 'name' in data:
            property.name = data['name']
        if 'description' in data:
            property.description = data['description']
        if 'address' in data:
            property.address = data['address']
        if 'price_per_night' in data:
            property.price_per_night = data['price_per_night']

        db.session.commit()
        return property

    def delete_property(self, property_id: int):
        """Delete a property."""
        property = self.get_property(property_id)
        db.session.delete(property)
        db.session.commit()
