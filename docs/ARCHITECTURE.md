# Architecture Deep Dive

## Table of Contents
- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Scalability & Performance](#scalability--performance)

## System Overview

Service Mesh Observatory is a cloud-native observability platform designed for production Kubernetes environments running Istio or Linkerd service meshes. The platform provides real-time monitoring, security analysis, and automated threat detection across distributed microservices architectures.

### Design Principles

1. **Zero Trust Security**: mTLS enforcement, RBAC policies, network segmentation
2. **Cloud Native**: Kubernetes-first design, container-based deployment, horizontal scalability
3. **Real-time Performance**: WebSocket-based updates, sub-100ms query latency, streaming analytics
4. **Production Ready**: Health probes, auto-scaling, graceful degradation, circuit breakers

## Component Architecture

### Frontend Layer

**Technology**: Next.js 14 (React 18), TypeScript, Tailwind CSS

The frontend is a server-side rendered (SSR) React application optimized for performance and SEO. It establishes WebSocket connections to the backend for real-time updates while maintaining REST API compatibility for initial data loading.

**Key Components**:
- **Landing Page**: Marketing page with feature highlights and architecture diagrams
- **Dashboard**: Real-time metrics visualization with auto-refresh
- **Service Topology Viewer**: Interactive graph showing service dependencies
- **Certificate Management**: mTLS certificate expiration tracking
- **Policy Tester**: Sandbox for validating authorization policies
- **Anomaly Dashboard**: Security threat visualization and investigation

**State Management**: Zustand for client-side state, React Query for server state caching

### Backend Layer

**Technology**: Python 3.11, FastAPI, asyncio

The backend is an asynchronous REST API built with FastAPI, providing high-throughput request handling and native async/await support for I/O-bound operations (Kubernetes API calls, Prometheus queries, database operations).

**Key Services**:

1. **Metrics Collector Service**
   - Background task running every 30 seconds
   - Queries Prometheus for service mesh metrics
   - Aggregates data across multiple clusters
   - Broadcasts updates via WebSocket to connected clients

2. **Topology Service**
   - Discovers services using Kubernetes API
   - Builds dependency graph from Istio metrics
   - Tracks service health and readiness
   - Caches topology data in Redis (5-minute TTL)

3. **Certificate Service**
   - Monitors mTLS certificate expiration
   - Queries Istio certificate chains
   - Generates expiration alerts (7/30/60/90 days)
   - Supports automated renewal triggers

4. **Policy Service**
   - Validates Istio AuthorizationPolicy YAML
   - Simulates policy enforcement without deployment
   - Tracks policy compliance across namespaces
   - Integrates with OPA for advanced validation

5. **Anomaly Detection Service**
   - Baseline traffic pattern learning
   - Statistical anomaly detection (Z-score, IQR)
   - ML-based classification (Isolation Forest)
   - Real-time scoring (0.0-1.0 anomaly score)

### Data Layer

**TimescaleDB** (PostgreSQL with time-series extensions):
- Stores historical metrics (7-day retention for high-res, 90-day for aggregates)
- Anomaly detection event log
- Audit trail for policy changes
- User authentication and session management

**Redis**:
- Real-time metrics cache
- WebSocket connection state
- Pub/Sub for multi-instance coordination
- Rate limiting and throttling

### Observability Stack

**Prometheus**:
- Scrapes Istio Envoy sidecar metrics (request rate, latency, errors)
- Collects istiod control plane metrics
- Application metrics from Observatory backend
- 15-second scrape interval, 15-day retention

**Jaeger**:
- Distributed tracing across service mesh
- Request flow visualization
- Latency hotspot identification
- Integration with Istio telemetry

**Loki**:
- Centralized log aggregation
- Label-based log querying
- Integration with Grafana
- 30-day log retention

**Grafana**:
- Pre-built dashboards for service mesh metrics
- Certificate health visualization
- Anomaly detection timeline
- Custom alerting rules

## Data Flow

### Real-time Metrics Flow

```
Envoy Sidecar → Prometheus → Metrics Collector → TimescaleDB
                    ↓                  ↓
                 Grafana          WebSocket → Frontend
```

1. Envoy sidecars expose metrics on port 15090
2. Prometheus scrapes metrics every 15 seconds
3. Metrics Collector queries Prometheus every 30 seconds
4. Aggregated metrics stored in TimescaleDB
5. WebSocket broadcasts push updates to connected clients
6. Grafana queries Prometheus for visualization

### Topology Discovery Flow

```
Kubernetes API → Topology Service → Redis Cache → Frontend
                       ↓
              Prometheus (traffic data)
```

1. Topology Service lists Services and Pods via K8s API
2. Queries Prometheus for actual traffic flows (istio_requests_total)
3. Builds dependency graph with traffic volume
4. Caches in Redis for 5 minutes
5. REST API serves topology to frontend

### Anomaly Detection Flow

```
Prometheus → Anomaly Service → ML Model → TimescaleDB
                                   ↓
                            WebSocket Alert
```

1. Anomaly Service queries baseline metrics (7-day average)
2. Compares current metrics to baseline
3. Calculates Z-score and applies Isolation Forest
4. Scores above threshold (0.85) trigger alerts
5. Anomalies logged to TimescaleDB
6. Real-time alerts via WebSocket

## Security Architecture

### Zero Trust Implementation

**mTLS Everywhere**:
- Istio enforces STRICT mTLS mode in PeerAuthentication
- All service-to-service communication encrypted
- Certificate rotation every 90 days (Istio CA)
- Observatory monitors certificate expiration

**AuthorizationPolicy Enforcement**:
```yaml
# Example: Backend service only accepts traffic from Frontend
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  selector:
    matchLabels:
      app: observatory-backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/observatory/sa/observatory-frontend"]
```

**Network Policies**:
- Kubernetes NetworkPolicy restricts ingress/egress at L3/L4
- Istio AuthorizationPolicy controls L7 (HTTP methods, paths)
- Defense in depth: both layers required for communication

### RBAC Configuration

Observatory backend uses minimal Kubernetes RBAC permissions:
- **Read-only access** to services, pods, namespaces
- **Read-only access** to Istio CRDs (VirtualService, DestinationRule, AuthorizationPolicy)
- **No write permissions** to cluster resources (read-only observability)

### Secrets Management

- Database credentials: Kubernetes Secrets (base64 encoded)
- API keys: Mounted as environment variables from Secrets
- TLS certificates: cert-manager integration (auto-renewal)
- Production: Integration with HashiCorp Vault or AWS Secrets Manager

## Scalability & Performance

### Horizontal Pod Autoscaling (HPA)

**Backend**:
- Min replicas: 3
- Max replicas: 10
- CPU target: 70%
- Memory target: 80%

**Frontend**:
- Min replicas: 2
- Max replicas: 5
- CPU target: 70%

### Database Optimization

**TimescaleDB Hypertables**:
- Automatic partitioning by time (1-week chunks)
- Continuous aggregates for pre-computed metrics
- Data retention policies (auto-delete old data)
- Connection pooling (20 connections, 10 overflow)

### Caching Strategy

**Redis Caching**:
- Topology data: 5-minute TTL
- Prometheus query results: 1-minute TTL
- Certificate status: 15-minute TTL
- Cache hit ratio target: >80%

### Performance Targets

- API response time (P95): <100ms
- WebSocket message delivery: <50ms
- Topology discovery: <2 seconds
- Anomaly detection latency: <5 seconds
- Dashboard load time: <1 second

### Multi-Cluster Support

For monitoring multiple Kubernetes clusters:
1. Deploy Observatory instance per cluster (federated architecture)
2. Use Prometheus federation to aggregate cross-cluster metrics
3. Central Grafana instance queries all Prometheus instances
4. Shared TimescaleDB for unified anomaly detection

## Technology Decisions

### Why FastAPI?
- Native async/await for I/O-bound operations
- Automatic OpenAPI documentation
- Pydantic validation (type safety)
- Production-proven (Uber, Netflix)

### Why TimescaleDB?
- PostgreSQL compatibility (familiar SQL)
- Optimized for time-series workloads
- Continuous aggregates (pre-computed rollups)
- Better compression than vanilla PostgreSQL

### Why Next.js?
- Server-side rendering for SEO and performance
- API routes for BFF (Backend for Frontend) pattern
- Image optimization out-of-the-box
- Incremental static regeneration

### Why Istio over Linkerd?
- More mature AuthorizationPolicy API
- Better integration with Prometheus
- Wider enterprise adoption
- Advanced traffic management (weighted routing, mirroring)

Note: Platform supports both Istio and Linkerd with adapter pattern

## Deployment Architecture

### AWS EKS Deployment

```
ALB Ingress → Istio Gateway → Frontend (ClusterIP)
                    ↓
              Backend (ClusterIP) → RDS PostgreSQL (TimescaleDB)
                    ↓                      ↓
              ElastiCache Redis      S3 (backups)
```

### On-Premises Deployment

```
NGINX Ingress → Istio Gateway → Frontend (ClusterIP)
                      ↓
                Backend (ClusterIP) → PostgreSQL Pod
                      ↓                      ↓
                  Redis Pod            PersistentVolume
```

## Disaster Recovery

**Backup Strategy**:
- TimescaleDB: Daily full backup, hourly incremental
- Redis: Snapshot every 6 hours (RDB)
- Kubernetes manifests: GitOps (ArgoCD)

**Recovery Time Objective (RTO)**: 15 minutes
**Recovery Point Objective (RPO)**: 1 hour

**Failure Scenarios**:
1. **Backend pod failure**: HPA launches new replica within 30 seconds
2. **Database failure**: Restore from latest snapshot (RPO: 1 hour)
3. **Entire cluster failure**: Rebuild cluster from IaC, restore data from S3

## Future Enhancements

1. **Multi-Tenancy**: Namespace isolation, per-tenant RBAC
2. **Advanced ML**: LSTM-based anomaly detection, predictive scaling
3. **Compliance Reporting**: Automated NIST 800-53, SOC 2 evidence generation
4. **Chaos Engineering**: Fault injection testing via Istio
5. **Cost Optimization**: Resource right-sizing recommendations based on actual usage
