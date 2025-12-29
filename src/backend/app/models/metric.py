"""
Metric Models
Database models for storing service mesh metrics (TimescaleDB hypertables)
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Index
from datetime import datetime

from app.models.base import Base, UUIDMixin


class ServiceMetric(Base, UUIDMixin):
    """
    Service-level metrics aggregated over time
    Designed for TimescaleDB hypertable (time-partitioned)
    """

    __tablename__ = "service_metrics"

    # Time column (TimescaleDB hypertable partition key)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)

    # Service identification
    service_name = Column(String(255), nullable=False, index=True)
    namespace = Column(String(255), nullable=False, index=True)

    # Traffic metrics
    request_rate = Column(Float, nullable=True)  # requests per second
    error_rate = Column(Float, nullable=True)  # percentage (0-100)
    success_rate = Column(Float, nullable=True)  # percentage (0-100)

    # Latency metrics (milliseconds)
    latency_p50 = Column(Float, nullable=True)
    latency_p95 = Column(Float, nullable=True)
    latency_p99 = Column(Float, nullable=True)
    latency_avg = Column(Float, nullable=True)

    # Connection metrics
    active_connections = Column(Integer, nullable=True)
    connection_errors = Column(Integer, nullable=True)

    # mTLS metrics
    mtls_requests = Column(Integer, nullable=True)
    plaintext_requests = Column(Integer, nullable=True)

    # Resource metrics
    cpu_usage = Column(Float, nullable=True)  # percentage
    memory_usage = Column(Float, nullable=True)  # percentage

    # Response code breakdown
    response_codes = Column(JSON, nullable=True)  # {"200": 1000, "500": 5}

    __table_args__ = (
        Index('idx_service_metrics_time_service', 'timestamp', 'service_name', 'namespace'),
    )

    def __repr__(self):
        return f"<ServiceMetric {self.service_name} @ {self.timestamp}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "service": self.service_name,
            "namespace": self.namespace,
            "request_rate": self.request_rate,
            "error_rate": self.error_rate,
            "latency_p50": self.latency_p50,
            "latency_p95": self.latency_p95,
            "latency_p99": self.latency_p99,
            "active_connections": self.active_connections,
            "mtls_requests": self.mtls_requests
        }


class MetricSnapshot(Base, UUIDMixin):
    """
    Point-in-time snapshot of overall mesh health
    Used for anomaly detection baseline and dashboard summary
    """

    __tablename__ = "metric_snapshots"

    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)

    # Mesh-wide aggregates
    total_services = Column(Integer, nullable=True)
    healthy_services = Column(Integer, nullable=True)
    total_pods = Column(Integer, nullable=True)

    # Overall traffic
    mesh_request_rate = Column(Float, nullable=True)
    mesh_error_rate = Column(Float, nullable=True)
    mesh_latency_p95 = Column(Float, nullable=True)

    # Security metrics
    mtls_coverage = Column(Float, nullable=True)  # percentage
    policy_compliance = Column(Float, nullable=True)  # percentage

    # Certificate health
    certs_expiring_7d = Column(Integer, nullable=True)
    certs_expiring_30d = Column(Integer, nullable=True)
    total_certificates = Column(Integer, nullable=True)

    # Anomaly summary
    active_anomalies = Column(Integer, nullable=True)
    critical_anomalies = Column(Integer, nullable=True)

    # Full snapshot data
    raw_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<MetricSnapshot @ {self.timestamp}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "total_services": self.total_services,
            "healthy_services": self.healthy_services,
            "mesh_request_rate": self.mesh_request_rate,
            "mesh_error_rate": self.mesh_error_rate,
            "mesh_latency_p95": self.mesh_latency_p95,
            "mtls_coverage": self.mtls_coverage,
            "certs_expiring_7d": self.certs_expiring_7d,
            "active_anomalies": self.active_anomalies
        }
