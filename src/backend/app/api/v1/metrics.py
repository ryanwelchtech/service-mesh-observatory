"""
Metrics Endpoints
Query and aggregate Prometheus metrics for service mesh monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.services.prometheus_service import prometheus_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/overview", response_model=Dict[str, Any])
async def get_metrics_overview():
    """
    Get high-level metrics overview
    Returns request rate, error rate, and latency across the mesh
    """
    try:
        metrics = await prometheus_service.get_mesh_overview()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_rate": metrics["request_rate"],
            "error_rate": metrics["error_rate"],
            "p50_latency_ms": metrics["p50_latency"],
            "p95_latency_ms": metrics["p95_latency"],
            "p99_latency_ms": metrics["p99_latency"],
            "active_connections": metrics["active_connections"]
        }
    except Exception as e:
        logger.error("Failed to fetch metrics overview", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/service/{service_name}", response_model=Dict[str, Any])
async def get_service_metrics(
    service_name: str,
    namespace: str = Query(default="default"),
    duration: str = Query(default="1h", description="Time range (e.g., 1h, 6h, 24h)")
):
    """Get detailed metrics for a specific service"""
    try:
        metrics = await prometheus_service.get_service_metrics(
            service_name, namespace, duration
        )
        return {
            "service": service_name,
            "namespace": namespace,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error("Failed to fetch service metrics", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch service metrics: {str(e)}")


@router.get("/traffic", response_model=Dict[str, Any])
async def get_traffic_metrics(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    duration: str = Query(default="1h")
):
    """
    Get traffic metrics between services
    If source/destination not specified, returns all traffic
    """
    try:
        traffic = await prometheus_service.get_traffic_metrics(source, destination, duration)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "traffic": traffic
        }
    except Exception as e:
        logger.error("Failed to fetch traffic metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch traffic metrics: {str(e)}")


@router.get("/latency/histogram", response_model=Dict[str, Any])
async def get_latency_histogram(
    service_name: Optional[str] = None,
    namespace: str = Query(default="default"),
    duration: str = Query(default="1h")
):
    """Get latency distribution histogram"""
    try:
        histogram = await prometheus_service.get_latency_histogram(
            service_name, namespace, duration
        )
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "histogram": histogram
        }
    except Exception as e:
        logger.error("Failed to fetch latency histogram", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch latency histogram: {str(e)}")


@router.get("/error-rate", response_model=Dict[str, Any])
async def get_error_rate(
    service_name: Optional[str] = None,
    namespace: str = Query(default="default"),
    duration: str = Query(default="1h")
):
    """Get error rate breakdown by service and status code"""
    try:
        errors = await prometheus_service.get_error_rates(service_name, namespace, duration)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "error_rates": errors
        }
    except Exception as e:
        logger.error("Failed to fetch error rates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch error rates: {str(e)}")
