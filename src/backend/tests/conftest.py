"""
Pytest Configuration and Fixtures
Shared test fixtures for all test modules
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator, Dict, Any

from app.main import app
from app.core.security import create_access_token, get_password_hash


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Generate a valid admin JWT token for testing"""
    token_data = {
        "sub": "test-admin-001",
        "email": "admin@test.com",
        "role": "admin"
    }
    return create_access_token(data=token_data)


@pytest.fixture(scope="session")
def viewer_token() -> str:
    """Generate a valid viewer JWT token for testing"""
    token_data = {
        "sub": "test-viewer-001",
        "email": "viewer@test.com",
        "role": "viewer"
    }
    return create_access_token(data=token_data)


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """HTTP headers with admin authentication"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def viewer_headers(viewer_token: str) -> Dict[str, str]:
    """HTTP headers with viewer authentication"""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user registration data"""
    return {
        "email": "newuser@test.com",
        "password": "securePassword123!",
        "name": "Test User"
    }


@pytest.fixture
def sample_policy_yaml() -> str:
    """Sample Istio AuthorizationPolicy YAML"""
    return """
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: test-policy
  namespace: default
spec:
  selector:
    matchLabels:
      app: test-app
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/test-sa"]
"""
