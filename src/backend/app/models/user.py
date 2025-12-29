"""
User Model
Database model for user authentication and authorization
"""

from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin):
    """User account model"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # API key for programmatic access
    api_key_hash = Column(String(255), nullable=True)

    # Last login tracking
    last_login = Column(String(50), nullable=True)  # ISO timestamp

    # Relationship to audit logs
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"

    def to_dict(self):
        """Convert to dictionary (excluding sensitive fields)"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login
        }
