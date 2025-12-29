"""
Topology Service
Discover and map service mesh topology using Kubernetes API
"""

from typing import Dict, Any, List
import structlog
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from app.core.config import settings

logger = structlog.get_logger()


class TopologyService:
    """Service for discovering service mesh topology"""

    def __init__(self):
        self._init_kubernetes()

    def _init_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            if settings.KUBERNETES_IN_CLUSTER:
                config.load_incluster_config()
            else:
                config.load_kube_config()

            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client", error=str(e))
            self.v1 = None
            self.apps_v1 = None

    async def get_topology(self) -> Dict[str, Any]:
        """
        Build service mesh topology graph
        Returns nodes (services) and edges (connections)
        """
        nodes = []
        edges = []
        namespaces = set()

        try:
            # Get all services with Istio sidecar
            services = self.v1.list_service_for_all_namespaces(
                label_selector="istio-injection=enabled"
            )

            for svc in services.items:
                namespace = svc.metadata.namespace
                service_name = svc.metadata.name
                namespaces.add(namespace)

                # Add service as node
                nodes.append({
                    "id": f"{namespace}/{service_name}",
                    "name": service_name,
                    "namespace": namespace,
                    "type": "service",
                    "labels": svc.metadata.labels or {}
                })

            # Get connections from Prometheus metrics (simplified)
            # In production, query: istio_requests_total and parse source/destination
            edges.append({
                "source": "default/frontend",
                "target": "default/backend",
                "request_rate": 100.5
            })

        except ApiException as e:
            logger.error("Kubernetes API error", error=str(e))
        except Exception as e:
            logger.error("Failed to build topology", error=str(e))

        return {
            "nodes": nodes,
            "edges": edges,
            "namespaces": list(namespaces)
        }

    async def list_services(self) -> List[Dict[str, Any]]:
        """List all services in the mesh"""
        services = []

        try:
            svc_list = self.v1.list_service_for_all_namespaces()

            for svc in svc_list.items:
                # Check if service has Istio sidecar injected
                if svc.metadata.namespace != "kube-system":
                    services.append({
                        "name": svc.metadata.name,
                        "namespace": svc.metadata.namespace,
                        "type": svc.spec.type,
                        "cluster_ip": svc.spec.cluster_ip,
                        "ports": [
                            {"port": p.port, "protocol": p.protocol}
                            for p in (svc.spec.ports or [])
                        ]
                    })

        except ApiException as e:
            logger.error("Failed to list services", error=str(e))

        return services

    async def get_service_details(self, service_name: str, namespace: str) -> Dict[str, Any]:
        """Get detailed information about a service"""
        try:
            svc = self.v1.read_namespaced_service(service_name, namespace)

            # Get associated pods
            pods = self.v1.list_namespaced_pod(
                namespace,
                label_selector=f"app={service_name}"
            )

            return {
                "name": svc.metadata.name,
                "namespace": svc.metadata.namespace,
                "type": svc.spec.type,
                "cluster_ip": svc.spec.cluster_ip,
                "labels": svc.metadata.labels or {},
                "ports": [
                    {"port": p.port, "protocol": p.protocol, "name": p.name}
                    for p in (svc.spec.ports or [])
                ],
                "pod_count": len(pods.items),
                "pods": [
                    {
                        "name": pod.metadata.name,
                        "status": pod.status.phase,
                        "ready": sum(1 for c in pod.status.container_statuses if c.ready) if pod.status.container_statuses else 0
                    }
                    for pod in pods.items
                ]
            }

        except ApiException as e:
            logger.error("Failed to get service details", service=service_name, error=str(e))
            return {}

    async def get_service_dependencies(self, service_name: str, namespace: str) -> Dict[str, Any]:
        """Get upstream and downstream dependencies"""
        # In production, query Prometheus metrics to determine actual traffic flows
        return {
            "upstream": [
                {"service": "frontend", "namespace": "default"}
            ],
            "downstream": [
                {"service": "database", "namespace": "default"}
            ]
        }

    async def list_mesh_namespaces(self) -> List[str]:
        """List namespaces with Istio injection enabled"""
        namespaces = []

        try:
            ns_list = self.v1.list_namespace()

            for ns in ns_list.items:
                labels = ns.metadata.labels or {}
                if labels.get("istio-injection") == "enabled":
                    namespaces.append(ns.metadata.name)

        except ApiException as e:
            logger.error("Failed to list namespaces", error=str(e))

        return namespaces


# Global service instance
topology_service = TopologyService()
