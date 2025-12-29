"""
Configuration management using Pydantic Settings
Loads from environment variables with validation
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Service Mesh Observatory"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = "postgresql://observatory:observatory@localhost:5432/observatory"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Prometheus
    PROMETHEUS_URL: str = "http://localhost:9090"
    PROMETHEUS_SCRAPE_INTERVAL: int = 15  # seconds

    # Jaeger
    JAEGER_ENDPOINT: str = "http://localhost:16686"
    JAEGER_QUERY_LIMIT: int = 100

    # Loki
    LOKI_URL: str = "http://localhost:3100"

    # Istio
    ISTIO_API_ENDPOINT: str = "https://localhost:15014"
    ISTIO_NAMESPACE: str = "istio-system"

    # Kubernetes
    KUBERNETES_IN_CLUSTER: bool = False
    KUBERNETES_NAMESPACE: str = "default"

    # Metrics Collection
    METRICS_COLLECTION_INTERVAL: int = 30  # seconds
    ANOMALY_DETECTION_THRESHOLD: float = 0.85
    CERT_EXPIRY_WARNING_DAYS: List[int] = [7, 30, 60, 90]

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
