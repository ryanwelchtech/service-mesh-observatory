"""
API Endpoint Tests
Unit tests for service mesh observatory API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client: TestClient):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data

    def test_metrics_endpoint(self, client: TestClient):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "observatory" in response.text or "python" in response.text


class TestTopologyEndpoints:
    """Test topology API endpoints"""

    def test_get_topology(self, client: TestClient):
        """Test getting service mesh topology"""
        response = client.get("/api/v1/topology/")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "nodes" in data
        assert "edges" in data

    def test_list_services(self, client: TestClient):
        """Test listing services"""
        response = client.get("/api/v1/topology/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_namespaces(self, client: TestClient):
        """Test listing mesh namespaces"""
        response = client.get("/api/v1/topology/namespaces")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestMetricsEndpoints:
    """Test metrics API endpoints"""

    def test_get_metrics_overview(self, client: TestClient):
        """Test getting metrics overview"""
        response = client.get("/api/v1/metrics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "request_rate" in data
        assert "error_rate" in data

    def test_get_traffic_metrics(self, client: TestClient):
        """Test getting traffic metrics"""
        response = client.get("/api/v1/metrics/traffic")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "traffic" in data


class TestCertificateEndpoints:
    """Test certificate API endpoints"""

    def test_get_all_certificates(self, client: TestClient):
        """Test getting all certificates"""
        response = client.get("/api/v1/certificates/")
        assert response.status_code == 200
        data = response.json()
        assert "certificates" in data
        assert "total_certificates" in data

    def test_get_expiring_certificates(self, client: TestClient):
        """Test getting expiring certificates"""
        response = client.get("/api/v1/certificates/expiring?days=30")
        assert response.status_code == 200
        data = response.json()
        assert "threshold_days" in data
        assert "expiring_certificates" in data

    def test_get_certificate_health(self, client: TestClient):
        """Test getting certificate health status"""
        response = client.get("/api/v1/certificates/health")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert "status" in data


class TestPolicyEndpoints:
    """Test policy API endpoints"""

    def test_list_policies(self, client: TestClient):
        """Test listing authorization policies"""
        response = client.get("/api/v1/policies/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_compliance_status(self, client: TestClient):
        """Test getting policy compliance status"""
        response = client.get("/api/v1/policies/compliance/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_services" in data
        assert "compliance_percentage" in data

    def test_validate_policy_valid(self, client: TestClient, sample_policy_yaml):
        """Test validating a valid policy YAML"""
        response = client.post(
            "/api/v1/policies/validate",
            json={"policy_yaml": sample_policy_yaml}
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data

    def test_validate_policy_invalid(self, client: TestClient):
        """Test validating an invalid policy YAML"""
        response = client.post(
            "/api/v1/policies/validate",
            json={"policy_yaml": "invalid: yaml: content:"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


class TestAnomalyEndpoints:
    """Test anomaly API endpoints"""

    def test_get_recent_anomalies(self, client: TestClient):
        """Test getting recent anomalies"""
        response = client.get("/api/v1/anomalies/")
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
        assert "count" in data

    def test_get_anomaly_types(self, client: TestClient):
        """Test getting anomaly types"""
        response = client.get("/api/v1/anomalies/types")
        assert response.status_code == 200
        types = response.json()
        assert isinstance(types, list)
        assert len(types) > 0
        assert "type" in types[0]
        assert "description" in types[0]

    def test_get_anomaly_statistics(self, client: TestClient):
        """Test getting anomaly statistics"""
        response = client.get("/api/v1/anomalies/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_severity" in data
        assert "by_type" in data
