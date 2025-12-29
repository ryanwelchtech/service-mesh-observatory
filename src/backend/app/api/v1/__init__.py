"""
API v1 Router
Aggregates all API endpoint routers
"""

from fastapi import APIRouter
from app.api.v1 import auth, topology, metrics, certificates, policies, anomalies

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(topology.router, prefix="/topology", tags=["Topology"])
router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
router.include_router(certificates.router, prefix="/certificates", tags=["Certificates"])
router.include_router(policies.router, prefix="/policies", tags=["Policies"])
router.include_router(anomalies.router, prefix="/anomalies", tags=["Anomalies"])
