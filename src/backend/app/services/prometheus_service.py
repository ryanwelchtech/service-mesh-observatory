"""
Prometheus Service
Query Prometheus for service mesh metrics
"""

import aiohttp
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime, timedelta

from app.core.config import settings

logger = structlog.get_logger()


class PrometheusService:
    """Service for querying Prometheus metrics"""

    def __init__(self):
        self.base_url = settings.PROMETHEUS_URL

    async def _query(self, query: str) -> Dict[str, Any]:
        """Execute Prometheus PromQL query"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/query",
                    params={"query": query}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error("Prometheus query failed", status=response.status)
                        return {"status": "error", "data": {}}
        except Exception as e:
            logger.error("Failed to query Prometheus", error=str(e))
            return {"status": "error", "data": {}}

    async def _query_range(self, query: str, start: datetime, end: datetime, step: str = "15s") -> Dict[str, Any]:
        """Execute Prometheus range query"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/query_range",
                    params={
                        "query": query,
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "step": step
                    }
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "data": {}}
        except Exception as e:
            logger.error("Failed to query Prometheus range", error=str(e))
            return {"status": "error", "data": {}}

    async def get_mesh_overview(self) -> Dict[str, Any]:
        """Get high-level mesh metrics"""
        # Request rate (requests per second across mesh)
        request_rate_query = 'sum(rate(istio_requests_total[5m]))'

        # Error rate (percentage)
        error_rate_query = 'sum(rate(istio_requests_total{response_code=~"5.."}[5m])) / sum(rate(istio_requests_total[5m])) * 100'

        # Latency percentiles
        p50_query = 'histogram_quantile(0.50, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))'
        p95_query = 'histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))'
        p99_query = 'histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))'

        # Active connections
        connections_query = 'sum(envoy_cluster_upstream_cx_active)'

        # Execute queries
        request_rate = await self._query(request_rate_query)
        error_rate = await self._query(error_rate_query)
        p50 = await self._query(p50_query)
        p95 = await self._query(p95_query)
        p99 = await self._query(p99_query)
        connections = await self._query(connections_query)

        return {
            "request_rate": self._extract_value(request_rate),
            "error_rate": self._extract_value(error_rate),
            "p50_latency": self._extract_value(p50),
            "p95_latency": self._extract_value(p95),
            "p99_latency": self._extract_value(p99),
            "active_connections": self._extract_value(connections)
        }

    async def get_service_metrics(self, service_name: str, namespace: str, duration: str) -> Dict[str, Any]:
        """Get metrics for a specific service"""
        query = f'''
            sum(rate(istio_requests_total{{
                destination_service_name="{service_name}",
                destination_service_namespace="{namespace}"
            }}[5m]))
        '''

        result = await self._query(query)

        return {
            "request_rate": self._extract_value(result),
            "service": service_name,
            "namespace": namespace
        }

    async def get_traffic_metrics(self, source: Optional[str], destination: Optional[str], duration: str) -> List[Dict[str, Any]]:
        """Get traffic flow between services"""
        query = 'sum(rate(istio_requests_total[5m])) by (source_workload, destination_service_name)'

        if source:
            query = f'sum(rate(istio_requests_total{{source_workload="{source}"}}[5m])) by (source_workload, destination_service_name)'

        result = await self._query(query)

        # Parse result into traffic flows
        traffic_flows = []
        if result.get("status") == "success":
            for item in result.get("data", {}).get("result", []):
                metric = item.get("metric", {})
                value = item.get("value", [0, "0"])

                traffic_flows.append({
                    "source": metric.get("source_workload", "unknown"),
                    "destination": metric.get("destination_service_name", "unknown"),
                    "request_rate": float(value[1]) if len(value) > 1 else 0
                })

        return traffic_flows

    async def get_latency_histogram(self, service_name: Optional[str], namespace: str, duration: str) -> Dict[str, Any]:
        """Get latency distribution"""
        if service_name:
            query = f'''
                histogram_quantile(0.95,
                    sum(rate(istio_request_duration_milliseconds_bucket{{
                        destination_service_name="{service_name}",
                        destination_service_namespace="{namespace}"
                    }}[5m])) by (le)
                )
            '''
        else:
            query = 'histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))'

        result = await self._query(query)

        return {
            "p95_latency": self._extract_value(result)
        }

    async def get_error_rates(self, service_name: Optional[str], namespace: str, duration: str) -> List[Dict[str, Any]]:
        """Get error rates by service and status code"""
        if service_name:
            query = f'''
                sum(rate(istio_requests_total{{
                    destination_service_name="{service_name}",
                    destination_service_namespace="{namespace}",
                    response_code=~"5.."
                }}[5m])) by (response_code)
            '''
        else:
            query = 'sum(rate(istio_requests_total{response_code=~"5.."}[5m])) by (response_code, destination_service_name)'

        result = await self._query(query)

        errors = []
        if result.get("status") == "success":
            for item in result.get("data", {}).get("result", []):
                metric = item.get("metric", {})
                value = item.get("value", [0, "0"])

                errors.append({
                    "response_code": metric.get("response_code", "unknown"),
                    "service": metric.get("destination_service_name", "unknown"),
                    "error_rate": float(value[1]) if len(value) > 1 else 0
                })

        return errors

    def _extract_value(self, prometheus_response: Dict[str, Any]) -> float:
        """Extract scalar value from Prometheus response"""
        try:
            if prometheus_response.get("status") == "success":
                result = prometheus_response.get("data", {}).get("result", [])
                if result and len(result) > 0:
                    value = result[0].get("value", [0, "0"])
                    return float(value[1]) if len(value) > 1 else 0.0
        except Exception as e:
            logger.error("Failed to extract Prometheus value", error=str(e))

        return 0.0


# Global service instance
prometheus_service = PrometheusService()
