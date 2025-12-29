"""
Certificate Model
Database model for tracking mTLS certificate status and history
"""

from sqlalchemy import Column, String, DateTime, Boolean, Enum, Text
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class CertStatus(enum.Enum):
    """Certificate status"""
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class Certificate(Base, UUIDMixin, TimestampMixin):
    """mTLS certificate tracking"""

    __tablename__ = "certificates"

    # Service identification
    service_name = Column(String(255), nullable=False, index=True)
    namespace = Column(String(255), nullable=False, index=True)
    pod_name = Column(String(255), nullable=True)

    # Certificate details
    serial_number = Column(String(255), nullable=True)
    issuer = Column(String(500), nullable=True)
    subject = Column(String(500), nullable=True)
    san = Column(Text, nullable=True)  # Subject Alternative Names

    # Validity
    issued_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    days_until_expiry = Column(String(10), nullable=True)

    # Status
    status = Column(Enum(CertStatus), default=CertStatus.VALID, nullable=False, index=True)
    last_checked = Column(DateTime, nullable=True)

    # Certificate chain info
    chain_valid = Column(Boolean, default=True, nullable=False)
    chain_length = Column(String(5), nullable=True)

    # Fingerprints for tracking
    sha256_fingerprint = Column(String(64), nullable=True, unique=True)

    def __repr__(self):
        return f"<Certificate {self.service_name}/{self.namespace} - {self.status.value}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "service": self.service_name,
            "namespace": self.namespace,
            "issuer": self.issuer,
            "subject": self.subject,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "days_until_expiry": self.days_until_expiry,
            "status": self.status.value,
            "chain_valid": self.chain_valid,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None
        }
