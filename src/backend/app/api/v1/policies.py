"""
Authorization Policy Endpoints
Test and validate Istio AuthorizationPolicy configurations
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from datetime import datetime
import structlog

from app.services.policy_service import policy_service
from app.schemas.policy import PolicyTestRequest, PolicyValidationResult

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_policies(namespace: str = None):
    """List all authorization policies in the mesh"""
    try:
        policies = await policy_service.list_policies(namespace)
        return policies
    except Exception as e:
        logger.error("Failed to list policies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list policies: {str(e)}")


@router.get("/{policy_name}", response_model=Dict[str, Any])
async def get_policy(policy_name: str, namespace: str = "default"):
    """Get specific authorization policy details"""
    try:
        policy = await policy_service.get_policy(policy_name, namespace)
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_name} not found")
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch policy", policy=policy_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch policy: {str(e)}")


@router.post("/test", response_model=PolicyValidationResult)
async def test_policy(request: PolicyTestRequest = Body(...)):
    """
    Test authorization policy in sandbox mode
    Validates policy syntax and simulates enforcement without applying
    """
    try:
        result = await policy_service.test_policy(request)
        return result
    except Exception as e:
        logger.error("Failed to test policy", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to test policy: {str(e)}")


@router.post("/validate", response_model=Dict[str, Any])
async def validate_policy(policy_yaml: str = Body(..., embed=True)):
    """
    Validate policy YAML syntax and best practices
    Returns validation errors and warnings
    """
    try:
        validation = await policy_service.validate_policy_syntax(policy_yaml)
        return {
            "valid": validation["valid"],
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
            "suggestions": validation.get("suggestions", [])
        }
    except Exception as e:
        logger.error("Failed to validate policy", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to validate policy: {str(e)}")


@router.get("/compliance/status", response_model=Dict[str, Any])
async def get_compliance_status():
    """
    Get policy compliance status across the mesh
    Returns services with/without authorization policies
    """
    try:
        compliance = await policy_service.get_compliance_status()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_services": compliance["total_services"],
            "services_with_policies": compliance["services_with_policies"],
            "services_without_policies": compliance["services_without_policies"],
            "compliance_percentage": compliance["compliance_percentage"],
            "non_compliant_services": compliance["non_compliant_services"]
        }
    except Exception as e:
        logger.error("Failed to fetch compliance status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch compliance status: {str(e)}")


@router.get("/peer-authentication", response_model=List[Dict[str, Any]])
async def list_peer_authentication_policies(namespace: str = None):
    """List PeerAuthentication policies (mTLS enforcement)"""
    try:
        policies = await policy_service.list_peer_authentication(namespace)
        return policies
    except Exception as e:
        logger.error("Failed to list peer authentication policies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list peer authentication: {str(e)}")
