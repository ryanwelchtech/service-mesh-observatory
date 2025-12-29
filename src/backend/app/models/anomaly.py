"""
Anomaly Model
Database models for storing detected anomalies and threat events
"""

from sqlalchemy import Column, String, Float, Boolean, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class AnomalyType(enum.Enum):
    """Types of detected anomalies"""
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"
    REQUEST_SPIKE = "request_spike"
    ERROR_SPIKE = "error_spike"
    LATENCY_SPIKE = "latency_spike"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PORT_SCAN = "port_scan"
    CERTIFICATE_ISSUE = "certificate_issue"
    POLICY_VIOLATION = "policy_violation"
    UNKNOWN = "unknown"


class Severity(enum.Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Anomaly(Base, UUIDMixin, TimestampMixin):
    """Detected anomaly record"""

    __tablename__ = "anomalies"

    # Anomaly classification
    anomaly_type = Column(Enum(AnomalyType), nullable=False, index=True)
    severity = Column(Enum(Severity), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0.0 to 1.0 anomaly score

    # Source identification
    service_name = Column(String(255), nullable=False, index=True)
    namespace = Column(String(255), nullable=False, index=True)
    pod_name = Column(String(255), nullable=True)
    source_ip = Column(String(45), nullable=True)  # IPv6 compatible

    # Description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Detection details
    detection_method = Column(String(100), nullable=True)  # e.g., "isolation_forest", "z_score"
    contributing_factors = Column(JSON, nullable=True)  # JSON array of factors

    # Metrics at time of detection
    metrics_snapshot = Column(JSON, nullable=True)

    # Status tracking
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(String(50), nullable=True)  # ISO timestamp
    acknowledgement_notes = Column(Text, nullable=True)

    # Resolution
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(String(50), nullable=True)  # ISO timestamp
    resolution_notes = Column(Text, nullable=True)

    # False positive tracking
    is_false_positive = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Anomaly {self.anomaly_type.value} - {self.service_name} ({self.severity.value})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.anomaly_type.value,
            "severity": self.severity.value,
            "score": self.score,
            "service": self.service_name,
            "namespace": self.namespace,
            "pod": self.pod_name,
            "title": self.title,
            "description": self.description,
            "detection_method": self.detection_method,
            "contributing_factors": self.contributing_factors,
            "is_acknowledged": self.is_acknowledged,
            "is_resolved": self.is_resolved,
            "is_false_positive": self.is_false_positive,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
