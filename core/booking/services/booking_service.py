from datetime import datetime
from core.database.postgres.models import Booking, Property, User
from core.database.postgres.database import db
from core.common.exceptions import ResourceNotFoundError, ValidationError

class BookingService:
    def create_booking(self, user_id: int, property_id: int, check_in_date: datetime, check_out_date: datetime) -> Booking:
        """Create a new booking."""
        # Validate property exists
        property = Property.query.get(property_id)
        if not property:
            raise ResourceNotFoundError("Property", str(property_id))

        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))

        # Calculate total price (example: days * price_per_night)
        days = (check_out_date - check_in_date).days
        if days <= 0:
            raise ValidationError("Check-out date must be after check-in date")
        
        total_price = days * property.price_per_night

        booking = Booking(
            user_id=user_id,
            property_id=property_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_price=total_price,
            status='pending'
        )

        db.session.add(booking)
        db.session.commit()

        return booking

    def get_booking(self, booking_id: int) -> Booking:
        """Get a booking by ID."""
        booking = Booking.query.get(booking_id)
        if not booking:
            raise ResourceNotFoundError("Booking", str(booking_id))
        return booking

    def get_user_bookings(self, user_id: int, page: int = 1, per_page: int = 10):
        """Get all bookings for a user."""
        return Booking.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page
        )

    def get_property_bookings(self, property_id: int, page: int = 1, per_page: int = 10):
        """Get all bookings for a property."""
        return Booking.query.filter_by(property_id=property_id).paginate(
            page=page, per_page=per_page
        )

    def update_booking_status(self, booking_id: int, status: str) -> Booking:
        """Update the status of a booking."""
        booking = self.get_booking(booking_id)
        
        valid_statuses = ['pending', 'confirmed', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        booking.status = status
        db.session.commit()

        return booking

    def cancel_booking(self, booking_id: int) -> Booking:
        """Cancel a booking."""
        return self.update_booking_status(booking_id, 'cancelled')
