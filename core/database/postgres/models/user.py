from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import UserMixin
from core.database.postgres.database import db
from core.common.auth import hash_password, verify_password

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    def __init__(self, email: str, password: str, first_name: str):
        self.email = email.lower()
        self.set_password(password)
        self.first_name = first_name

    def set_password(self, password: str) -> None:
        """Set hashed password."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return verify_password(self.password_hash, password)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return self.first_name

    def to_dict(self) -> dict:
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
