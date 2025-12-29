"""
Policy Service
Validate and test Istio Authorization Policies
"""

from typing import Dict, Any, List, Optional
import structlog
import yaml

from app.core.config import settings

logger = structlog.get_logger()


class PolicyService:
    """Service for managing authorization policies"""

    async def list_policies(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all authorization policies"""
        # In production, query Istio API for AuthorizationPolicy CRDs
        policies = [
            {
                "name": "frontend-allow",
                "namespace": "default",
                "action": "ALLOW",
                "rules": 2,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "name": "backend-deny-external",
                "namespace": "default",
                "action": "DENY",
                "rules": 1,
                "created_at": "2024-01-15T00:00:00Z"
            }
        ]

        if namespace:
            policies = [p for p in policies if p["namespace"] == namespace]

        return policies

    async def get_policy(self, policy_name: str, namespace: str) -> Dict[str, Any]:
        """Get specific policy details"""
        policies = await self.list_policies(namespace)

        for policy in policies:
            if policy["name"] == policy_name:
                # In production, fetch full policy specification
                return {
                    **policy,
                    "spec": {
                        "selector": {
                            "matchLabels": {"app": "frontend"}
                        },
                        "action": "ALLOW",
                        "rules": [
                            {
                                "from": [
                                    {"source": {"principals": ["cluster.local/ns/default/sa/gateway"]}}
                                ]
                            }
                        ]
                    }
                }

        return {}

    async def test_policy(self, request) -> Dict[str, Any]:
        """Test policy in sandbox mode"""
        # Simulate policy validation
        logger.info("Testing policy", policy_name=request.policy_name if hasattr(request, 'policy_name') else 'unknown')

        # In production, validate against Istio API or use policy simulator
        return {
            "valid": True,
            "test_results": [
                {
                    "source": "frontend",
                    "destination": "backend",
                    "allowed": True,
                    "matched_rule": "rule-1"
                }
            ],
            "warnings": [],
            "errors": []
        }

    async def validate_policy_syntax(self, policy_yaml: str) -> Dict[str, Any]:
        """Validate policy YAML syntax"""
        errors = []
        warnings = []
        suggestions = []

        try:
            # Parse YAML
            policy = yaml.safe_load(policy_yaml)

            # Validate structure
            if not isinstance(policy, dict):
                errors.append("Policy must be a YAML object")
                return {"valid": False, "errors": errors}

            # Check required fields
            if "apiVersion" not in policy:
                errors.append("Missing required field: apiVersion")

            if "kind" not in policy:
                errors.append("Missing required field: kind")
            elif policy["kind"] != "AuthorizationPolicy":
                errors.append(f"Expected kind: AuthorizationPolicy, got: {policy['kind']}")

            if "metadata" not in policy:
                errors.append("Missing required field: metadata")
            elif "name" not in policy.get("metadata", {}):
                errors.append("Missing required field: metadata.name")

            # Validate spec
            spec = policy.get("spec", {})
            if not spec:
                warnings.append("Empty spec - policy will not have any effect")

            # Best practice suggestions
            if not spec.get("selector"):
                suggestions.append("Consider adding selector to target specific workloads")

            if spec.get("action") == "ALLOW" and not spec.get("rules"):
                warnings.append("ALLOW action without rules will deny all traffic")

        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {str(e)}")
            return {"valid": False, "errors": errors}
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return {"valid": False, "errors": errors}

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }

    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get policy compliance status"""
        # In production, compare services against applied policies
        total_services = 10
        services_with_policies = 7

        return {
            "total_services": total_services,
            "services_with_policies": services_with_policies,
            "services_without_policies": total_services - services_with_policies,
            "compliance_percentage": (services_with_policies / total_services) * 100,
            "non_compliant_services": [
                {"name": "test-service", "namespace": "default"},
                {"name": "debug-pod", "namespace": "development"},
                {"name": "legacy-app", "namespace": "production"}
            ]
        }

    async def list_peer_authentication(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List PeerAuthentication policies"""
        # In production, query PeerAuthentication CRDs
        policies = [
            {
                "name": "default",
                "namespace": "istio-system",
                "mtls_mode": "STRICT",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "name": "permissive-mode",
                "namespace": "development",
                "mtls_mode": "PERMISSIVE",
                "created_at": "2024-02-01T00:00:00Z"
            }
        ]

        if namespace:
            policies = [p for p in policies if p["namespace"] == namespace]

        return policies


# Global service instance
policy_service = PolicyService()
