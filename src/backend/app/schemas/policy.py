"""
Policy Schemas
Pydantic models for policy testing and validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class PolicyTestRequest(BaseModel):
    """Request model for testing authorization policy"""
    policy_name: str = Field(..., description="Name of the policy to test")
    namespace: str = Field(default="default", description="Kubernetes namespace")
    test_scenarios: List[Dict[str, Any]] = Field(
        ...,
        description="List of test scenarios with source, destination, and expected result"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "policy_name": "frontend-allow",
                "namespace": "default",
                "test_scenarios": [
                    {
                        "source": "gateway",
                        "destination": "frontend",
                        "expected": "allowed"
                    }
                ]
            }
        }


class PolicyValidationResult(BaseModel):
    """Result of policy testing"""
    valid: bool = Field(..., description="Whether policy is valid")
    test_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Results of each test scenario"
    )
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    errors: List[str] = Field(default_factory=list, description="Validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "test_results": [
                    {
                        "source": "gateway",
                        "destination": "frontend",
                        "allowed": True,
                        "matched_rule": "rule-1"
                    }
                ],
                "warnings": [],
                "errors": []
            }
        }
