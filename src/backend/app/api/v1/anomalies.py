"""
Anomaly Detection Endpoints
ML-based detection of unusual traffic patterns and security threats
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from datetime import datetime
import structlog

from app.services.anomaly_service import anomaly_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_recent_anomalies(
    limit: int = Query(default=50, le=200),
    severity: str = Query(default=None, description="Filter by severity: low, medium, high, critical")
):
    """Get recent anomaly detections"""
    try:
        anomalies = await anomaly_service.get_recent_anomalies(limit, severity)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        logger.error("Failed to fetch anomalies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {str(e)}")


@router.get("/service/{service_name}", response_model=Dict[str, Any])
async def get_service_anomalies(
    service_name: str,
    namespace: str = Query(default="default"),
    duration: str = Query(default="24h")
):
    """Get anomalies detected for a specific service"""
    try:
        anomalies = await anomaly_service.get_service_anomalies(
            service_name, namespace, duration
        )
        return {
            "service": service_name,
            "namespace": namespace,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "anomalies": anomalies
        }
    except Exception as e:
        logger.error("Failed to fetch service anomalies", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch service anomalies: {str(e)}")


@router.get("/types", response_model=List[Dict[str, Any]])
async def get_anomaly_types():
    """Get list of anomaly types detected by the system"""
    return [
        {
            "type": "data_exfiltration",
            "description": "Unusual outbound data transfer volume",
            "severity": "critical"
        },
        {
            "type": "lateral_movement",
            "description": "Unexpected service-to-service communication",
            "severity": "high"
        },
        {
            "type": "request_spike",
            "description": "Abnormal increase in request rate",
            "severity": "medium"
        },
        {
            "type": "error_spike",
            "description": "Sudden increase in error responses",
            "severity": "high"
        },
        {
            "type": "latency_spike",
            "description": "Unusual increase in response latency",
            "severity": "medium"
        },
        {
            "type": "unauthorized_access",
            "description": "Multiple authentication/authorization failures",
            "severity": "critical"
        },
        {
            "type": "port_scan",
            "description": "Sequential connection attempts to multiple ports",
            "severity": "high"
        }
    ]


@router.get("/score/{service_name}", response_model=Dict[str, Any])
async def get_anomaly_score(
    service_name: str,
    namespace: str = Query(default="default")
):
    """
    Get real-time anomaly score for a service
    Score ranges from 0.0 (normal) to 1.0 (highly anomalous)
    """
    try:
        score_data = await anomaly_service.calculate_anomaly_score(service_name, namespace)
        return {
            "service": service_name,
            "namespace": namespace,
            "timestamp": datetime.utcnow().isoformat(),
            "anomaly_score": score_data["score"],
            "threshold": 0.85,
            "status": "anomalous" if score_data["score"] > 0.85 else "normal",
            "contributing_factors": score_data["factors"]
        }
    except Exception as e:
        logger.error("Failed to calculate anomaly score", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to calculate anomaly score: {str(e)}")


@router.post("/{anomaly_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_anomaly(anomaly_id: str, notes: str = None):
    """Acknowledge an anomaly detection (mark as reviewed)"""
    try:
        result = await anomaly_service.acknowledge_anomaly(anomaly_id, notes)
        return {
            "anomaly_id": anomaly_id,
            "acknowledged": result["success"],
            "acknowledged_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Failed to acknowledge anomaly", anomaly_id=anomaly_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge anomaly: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_anomaly_statistics(duration: str = Query(default="7d")):
    """Get anomaly detection statistics over time"""
    try:
        stats = await anomaly_service.get_statistics(duration)
        return {
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "total_anomalies": stats["total"],
            "by_severity": stats["by_severity"],
            "by_type": stats["by_type"],
            "acknowledged": stats["acknowledged"],
            "unacknowledged": stats["unacknowledged"]
        }
    except Exception as e:
        logger.error("Failed to fetch anomaly statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")
