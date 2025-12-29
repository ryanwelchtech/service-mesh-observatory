"""
Certificate Management Endpoints
Monitor mTLS certificate health and expiration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
import structlog

from app.services.certificate_service import certificate_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_all_certificates():
    """
    Get all mTLS certificates in the service mesh
    Returns certificate metadata and expiration status
    """
    try:
        certs = await certificate_service.get_all_certificates()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_certificates": len(certs),
            "certificates": certs
        }
    except Exception as e:
        logger.error("Failed to fetch certificates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch certificates: {str(e)}")


@router.get("/expiring", response_model=Dict[str, Any])
async def get_expiring_certificates(
    days: int = Query(default=30, description="Days until expiration threshold")
):
    """Get certificates expiring within specified days"""
    try:
        expiring = await certificate_service.get_expiring_certificates(days)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "threshold_days": days,
            "expiring_certificates": expiring,
            "count": len(expiring)
        }
    except Exception as e:
        logger.error("Failed to fetch expiring certificates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch expiring certificates: {str(e)}")


@router.get("/service/{service_name}", response_model=Dict[str, Any])
async def get_service_certificate(service_name: str, namespace: str = Query(default="default")):
    """Get certificate information for a specific service"""
    try:
        cert_info = await certificate_service.get_service_certificate(service_name, namespace)
        if not cert_info:
            raise HTTPException(
                status_code=404,
                detail=f"Certificate not found for service {service_name}"
            )
        return {
            "service": service_name,
            "namespace": namespace,
            "certificate": cert_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch service certificate", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch service certificate: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def get_certificate_health():
    """
    Get overall certificate health status
    Returns counts by expiration windows and health score
    """
    try:
        health = await certificate_service.get_certificate_health()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_score": health["health_score"],
            "expiring_within_7_days": health["expiring_7d"],
            "expiring_within_30_days": health["expiring_30d"],
            "expiring_within_60_days": health["expiring_60d"],
            "expiring_within_90_days": health["expiring_90d"],
            "total_certificates": health["total"],
            "status": health["status"]
        }
    except Exception as e:
        logger.error("Failed to fetch certificate health", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch certificate health: {str(e)}")


@router.post("/renew/{service_name}", response_model=Dict[str, Any])
async def trigger_certificate_renewal(service_name: str, namespace: str = Query(default="default")):
    """Trigger certificate renewal for a service (if supported by mesh)"""
    try:
        result = await certificate_service.trigger_renewal(service_name, namespace)
        return {
            "service": service_name,
            "namespace": namespace,
            "renewal_triggered": result["success"],
            "message": result["message"]
        }
    except Exception as e:
        logger.error("Failed to trigger certificate renewal", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger renewal: {str(e)}")
