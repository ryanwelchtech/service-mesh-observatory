"""
Service Mesh Topology Endpoints
Provides service discovery and topology visualization data
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import structlog

from app.services.topology_service import topology_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_service_topology():
    """
    Get complete service mesh topology
    Returns nodes (services) and edges (connections) for visualization
    """
    try:
        topology = await topology_service.get_topology()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "nodes": topology["nodes"],
            "edges": topology["edges"],
            "summary": {
                "total_services": len(topology["nodes"]),
                "total_connections": len(topology["edges"]),
                "namespaces": topology.get("namespaces", [])
            }
        }
    except Exception as e:
        logger.error("Failed to fetch topology", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch topology: {str(e)}")


@router.get("/services", response_model=List[Dict[str, Any]])
async def list_services():
    """List all discovered services in the mesh"""
    try:
        services = await topology_service.list_services()
        return services
    except Exception as e:
        logger.error("Failed to list services", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list services: {str(e)}")


@router.get("/services/{service_name}", response_model=Dict[str, Any])
async def get_service_details(service_name: str, namespace: str = "default"):
    """Get detailed information about a specific service"""
    try:
        service_info = await topology_service.get_service_details(service_name, namespace)
        if not service_info:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        return service_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch service details", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch service details: {str(e)}")


@router.get("/services/{service_name}/dependencies", response_model=Dict[str, Any])
async def get_service_dependencies(service_name: str, namespace: str = "default"):
    """Get upstream and downstream dependencies for a service"""
    try:
        dependencies = await topology_service.get_service_dependencies(service_name, namespace)
        return {
            "service": service_name,
            "namespace": namespace,
            "upstream": dependencies["upstream"],
            "downstream": dependencies["downstream"]
        }
    except Exception as e:
        logger.error("Failed to fetch dependencies", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch dependencies: {str(e)}")


@router.get("/namespaces", response_model=List[str])
async def list_namespaces():
    """List all namespaces with service mesh injection enabled"""
    try:
        namespaces = await topology_service.list_mesh_namespaces()
        return namespaces
    except Exception as e:
        logger.error("Failed to list namespaces", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list namespaces: {str(e)}")
