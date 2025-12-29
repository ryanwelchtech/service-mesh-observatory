"""
Audit Log Model
Database model for tracking all administrative and security actions
"""

from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class AuditAction(enum.Enum):
    """Types of auditable actions"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    TOKEN_REFRESH = "token_refresh"

    # User management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    ROLE_CHANGE = "role_change"

    # Policy actions
    POLICY_VIEW = "policy_view"
    POLICY_TEST = "policy_test"
    POLICY_VALIDATE = "policy_validate"

    # Anomaly actions
    ANOMALY_ACKNOWLEDGE = "anomaly_acknowledge"
    ANOMALY_RESOLVE = "anomaly_resolve"
    ANOMALY_FALSE_POSITIVE = "anomaly_false_positive"

    # Certificate actions
    CERT_RENEWAL_TRIGGER = "cert_renewal_trigger"

    # System actions
    CONFIG_CHANGE = "config_change"
    EXPORT_DATA = "export_data"
    API_ACCESS = "api_access"


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Audit log entry for compliance and security tracking"""

    __tablename__ = "audit_logs"

    # Actor
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)

    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)  # e.g., "anomaly", "policy", "user"
    resource_id = Column(String(255), nullable=True, index=True)

    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)

    # Outcome
    success = Column(String(5), default="true", nullable=False)  # "true" or "false"
    error_message = Column(Text, nullable=True)

    # Additional context
    details = Column(JSON, nullable=True)  # Flexible additional data
    old_value = Column(JSON, nullable=True)  # For tracking changes
    new_value = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action.value} by {self.user_email} @ {self.created_at}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "success": self.success == "true",
            "details": self.details
        }
