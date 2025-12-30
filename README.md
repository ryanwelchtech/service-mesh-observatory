# Service Mesh Observatory

[![CI](https://github.com/ryanwelchtech/service-mesh-observatory/workflows/CI/badge.svg)](https://github.com/ryanwelchtech/service-mesh-observatory/actions)
[![Security Scan](https://github.com/ryanwelchtech/service-mesh-observatory/workflows/Security%20Scan/badge.svg)](https://github.com/ryanwelchtech/service-mesh-observatory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Comprehensive observability and security platform for Istio/Linkerd service mesh deployments. Provides real-time visibility into mTLS certificate health, authorization policies, traffic patterns, and anomaly detection for microservices architectures.

## Architecture

```mermaid
graph TB
    subgraph "Service Mesh Observatory Platform"
        subgraph "Frontend Layer"
            UI[React Dashboard<br/>WebSocket Client]
        end

        subgraph "Backend Services"
            API[FastAPI Gateway<br/>Port 8000]
            WS[WebSocket Service<br/>Real-time Updates]
            Collector[Metrics Collector<br/>Prometheus Client]
        end

        subgraph "Data Layer"
            TSDB[(TimescaleDB<br/>Time-series Metrics)]
            Cache[(Redis<br/>Real-time Cache)]
        end

        subgraph "Monitoring Stack"
            Prom[Prometheus<br/>Metrics Storage]
            Jaeger[Jaeger<br/>Distributed Tracing]
            Loki[Loki<br/>Log Aggregation]
        end
    end

    subgraph "Istio Service Mesh"
        Istiod[Istiod Control Plane]
        Envoy1[Envoy Proxy<br/>Service A]
        Envoy2[Envoy Proxy<br/>Service B]
        Envoy3[Envoy Proxy<br/>Service C]
    end

    UI -->|REST/WebSocket| API
    API --> WS
    API --> Collector
    Collector -->|Query Metrics| Prom
    Collector -->|Query Traces| Jaeger
    Collector -->|Query Logs| Loki
    API --> TSDB
    WS --> Cache

    Prom -->|Scrape| Envoy1
    Prom -->|Scrape| Envoy2
    Prom -->|Scrape| Envoy3
    Prom -->|Scrape| Istiod

    Jaeger -->|Collect Spans| Envoy1
    Jaeger -->|Collect Spans| Envoy2
    Jaeger -->|Collect Spans| Envoy3

    Istiod -->|Control| Envoy1
    Istiod -->|Control| Envoy2
    Istiod -->|Control| Envoy3

    style UI fill:#3b82f6,stroke:#1e40af,color:#fff
    style API fill:#10b981,stroke:#059669,color:#fff
    style Istiod fill:#f59e0b,stroke:#d97706,color:#fff
```

## System Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant Prometheus
    participant Istio
    participant TimescaleDB

    User->>Dashboard: Access Observatory UI
    Dashboard->>API: WebSocket Connection
    API->>API: Authenticate & Authorize

    loop Real-time Monitoring
        API->>Prometheus: Query Service Mesh Metrics
        Prometheus-->>API: Traffic, Latency, Error Rates
        API->>Istio: Query mTLS Cert Status
        Istio-->>API: Certificate Expiration Data
        API->>TimescaleDB: Store Time-series Data
        API->>Dashboard: Push Real-time Updates
    end

    User->>Dashboard: Test Authorization Policy
    Dashboard->>API: POST /api/v1/policies/test
    API->>Istio: Apply Test Policy
    Istio-->>API: Validation Result
    API->>Dashboard: Policy Test Result
    Dashboard->>User: Display Success/Failure
```

## Screenshots

### Service Mesh Topology Visualization
Interactive graph showing all services, their connections, and real-time traffic flow with health indicators.

![Topology Visualization](screenshots/topology-visualization.png)

### Service Details Panel
Click any service node to view detailed metrics including RPS, latency, error rates, and mTLS status.

![Service Details](screenshots/topology-service-details.png)

### Dashboard Overview
Real-time metrics, alerts, certificate health status, and authorization policy monitoring.

![Dashboard](screenshots/dashboard-overview.png)

### Landing Page
Modern glassmorphism UI showcasing platform capabilities and tech stack.

![Landing Page](screenshots/landing-page.png)

## Key Features

- **Real-time Service Topology**: Interactive service mesh visualization with traffic flow heat maps, latency percentiles, and request rates updated via WebSocket
- **mTLS Certificate Management**: Automated tracking of certificate expiration across all workloads with 30/60/90-day alerts and renewal recommendations
- **Authorization Policy Testing**: Sandbox environment to validate Istio AuthorizationPolicy and PeerAuthentication before production deployment
- **Anomaly Detection**: Machine learning-based detection of unusual traffic patterns indicating data exfiltration, lateral movement, or DDoS attacks
- **Distributed Tracing Integration**: Jaeger trace correlation with service topology showing end-to-end request flows and bottleneck identification
- **Multi-Cluster Support**: Unified dashboard for monitoring service mesh deployments across multiple Kubernetes clusters

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router), React 18, TypeScript
- **Styling**: Tailwind CSS, Framer Motion animations
- **Visualization**: React Flow (topology), Recharts (metrics), D3.js (custom graphs)
- **Real-time**: WebSocket client, React Query for API state

### Backend
- **API**: Python 3.11, FastAPI, Pydantic v2
- **Real-time**: WebSocket server, Redis Pub/Sub
- **Data**: TimescaleDB, SQLAlchemy, Alembic migrations
- **Monitoring**: Prometheus client, Jaeger Python client

### Infrastructure
- **Orchestration**: Kubernetes 1.28+, Istio 1.20+
- **Observability**: Prometheus, Grafana, Jaeger, Loki
- **IaC**: Terraform (AWS EKS), Kustomize overlays
- **CI/CD**: GitHub Actions, Trivy security scanning

### Service Mesh
- **Control Plane**: Istio 1.20+ or Linkerd 2.14+
- **Data Plane**: Envoy Proxy with mTLS enabled
- **Policies**: AuthorizationPolicy, PeerAuthentication, RequestAuthentication

## Getting Started

### Prerequisites

- Kubernetes cluster (v1.28+) with Istio installed
- kubectl configured for cluster access
- Docker and Docker Compose
- Node.js 18+ and Python 3.11+

### Quick Start (Local Development)

```bash
# Clone repository
git clone https://github.com/ryanwelchtech/service-mesh-observatory.git
cd service-mesh-observatory

# Start dependencies (TimescaleDB, Redis, Prometheus)
docker-compose up -d

# Install backend dependencies
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In new terminal: Install frontend dependencies
cd src/frontend
npm install

# Start frontend dev server
npm run dev
```

Access the dashboard at `http://localhost:3000`

### Kubernetes Deployment

```bash
# Install Istio (if not already installed)
istioctl install --set profile=demo -y

# Enable Istio sidecar injection
kubectl label namespace default istio-injection=enabled

# Deploy monitoring stack
kubectl apply -k infrastructure/kubernetes/monitoring/

# Deploy Service Mesh Observatory
kubectl apply -k infrastructure/kubernetes/base/

# Port-forward to access UI
kubectl port-forward svc/observatory-frontend 3000:3000 -n observatory
```

## Deployment

### Production Deployment (AWS EKS)

```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init

# Deploy EKS cluster with Istio
terraform plan -out=tfplan
terraform apply tfplan

# Configure kubectl
aws eks update-kubeconfig --name service-mesh-observatory --region us-east-1

# Deploy application with Kustomize
kubectl apply -k infrastructure/kubernetes/overlays/production/
```

### Configuration

Key environment variables:

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@timescaledb:5432/observatory
REDIS_URL=redis://redis:6379/0
PROMETHEUS_URL=http://prometheus:9090
JAEGER_ENDPOINT=http://jaeger:16686
ISTIO_API_ENDPOINT=https://istiod.istio-system:15014

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Security Considerations

### Zero Trust Architecture
- mTLS enforcement for all service-to-service communication
- JWT-based authentication for API access with role-based access control (RBAC)
- Kubernetes RBAC policies limiting Observatory service account to read-only mesh observability

### Secure Deployment
- Non-root container execution (UID 1000)
- Read-only root filesystem with explicit volume mounts
- Network policies restricting ingress/egress to required services only
- Secrets managed via Kubernetes Secrets with encryption at rest

### Vulnerability Management
- Automated Trivy scanning in CI/CD pipeline blocking high/critical CVEs
- Base images rebuilt weekly to incorporate security patches
- Dependency scanning with Snyk for Python and npm packages

### Compliance
- Audit logging of all policy changes and administrative actions
- NIST 800-53 AC-2, AC-3, AU-2, SC-8 control alignment
- TLS 1.3 enforcement for all external communications

## Monitoring & Observability

### Metrics Exposed

```prometheus
# Service Mesh Observatory metrics
observatory_services_discovered_total
observatory_mtls_certificates_expiring_7d
observatory_anomaly_detections_total
observatory_policy_validations_total
observatory_api_request_duration_seconds

# Access Prometheus at http://localhost:9090
```

### Grafana Dashboards

Pre-built dashboards available in `monitoring/grafana/dashboards/`:
- Service Mesh Overview (traffic, latency, errors)
- mTLS Certificate Health
- Authorization Policy Compliance
- Anomaly Detection Alerts

Access Grafana: `kubectl port-forward svc/grafana 3001:3000 -n monitoring`

### Alerting Rules

Critical alerts configured in `monitoring/prometheus/rules.yaml`:
- Certificate expiring within 7 days
- Anomaly detection score > 0.85
- Service mesh control plane down
- Mutual TLS authentication failures > 5% of requests

## Documentation

- [Architecture Deep Dive](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Hardening](docs/SECURITY.md)
- [Operations Runbook](docs/RUNBOOK.md)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/anomaly-ml-model`)
3. Commit changes (`git commit -m 'Add LSTM-based anomaly detection'`)
4. Push to branch (`git push origin feature/anomaly-ml-model`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contact

**Ryan Welch**
Cloud & Systems Security Engineer
[GitHub](https://github.com/ryanwelchtech) | [LinkedIn](https://www.linkedin.com/in/ryanwelch54/)

---

Built with Kubernetes, Istio, FastAPI, Next.js, and a focus on Zero Trust security architecture.
