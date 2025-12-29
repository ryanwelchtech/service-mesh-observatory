# Deployment Guide

Complete guide for deploying Service Mesh Observatory to production Kubernetes environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [AWS EKS Deployment](#aws-eks-deployment)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Kubernetes cluster (v1.28+)
- kubectl (v1.28+)
- Helm (v3.12+) - optional
- Istio (v1.20+) or Linkerd (v2.14+)
- Docker (v24.0+)

### Required Kubernetes Resources
- **CPU**: 4 vCPU minimum (8 vCPU recommended)
- **Memory**: 8 GB minimum (16 GB recommended)
- **Storage**: 50 GB for TimescaleDB and metrics retention

### Access Requirements
- Kubernetes cluster admin access
- Container registry access (GHCR, ECR, or Docker Hub)
- DNS management (for production ingress)

## Local Development Setup

### Option 1: Docker Compose (Quickest)

```bash
# Clone repository
git clone https://github.com/ryanwelchtech/service-mesh-observatory.git
cd service-mesh-observatory

# Start all services
docker-compose up -d

# Wait for services to be healthy (2-3 minutes)
docker-compose ps

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
```

### Option 2: Local Kubernetes (Minikube/Kind)

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0

# Install Istio
istioctl install --set profile=demo -y

# Enable sidecar injection for default namespace
kubectl label namespace default istio-injection=enabled

# Deploy monitoring stack
kubectl create namespace monitoring
kubectl apply -f monitoring/kubernetes/ -n monitoring

# Deploy Observatory
kubectl apply -k infrastructure/kubernetes/base/

# Port-forward to access services
kubectl port-forward svc/observatory-frontend 3000:3000 -n observatory &
kubectl port-forward svc/observatory-backend 8000:8000 -n observatory &
kubectl port-forward svc/grafana 3001:3000 -n monitoring &
```

## Kubernetes Deployment

### Step 1: Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.20.0
export PATH=$PWD/bin:$PATH

# Install Istio with demo profile
istioctl install --set profile=demo -y

# Verify installation
kubectl get pods -n istio-system
```

### Step 2: Deploy Monitoring Stack

```bash
# Create monitoring namespace
kubectl create namespace monitoring
kubectl label namespace monitoring istio-injection=enabled

# Deploy Prometheus
kubectl apply -f monitoring/kubernetes/prometheus/ -n monitoring

# Deploy Grafana
kubectl apply -f monitoring/kubernetes/grafana/ -n monitoring

# Deploy Jaeger
kubectl apply -f monitoring/kubernetes/jaeger/ -n monitoring

# Verify deployment
kubectl get pods -n monitoring
```

### Step 3: Configure Secrets

```bash
# Create secrets from template
cp infrastructure/kubernetes/base/secrets.yaml.example \
   infrastructure/kubernetes/base/secrets.yaml

# Edit secrets with actual values
# Replace CHANGE_ME placeholders
vim infrastructure/kubernetes/base/secrets.yaml

# Apply secrets
kubectl apply -f infrastructure/kubernetes/base/secrets.yaml
```

### Step 4: Deploy Observatory

```bash
# Deploy using Kustomize
kubectl apply -k infrastructure/kubernetes/base/

# Verify deployment
kubectl get pods -n observatory
kubectl get svc -n observatory

# Check pod status
kubectl describe pod -l app=observatory-backend -n observatory
```

### Step 5: Configure Ingress

```bash
# Create TLS certificate (production)
kubectl create secret tls observatory-tls-cert \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n observatory

# Apply Istio Gateway
kubectl apply -f infrastructure/kubernetes/base/istio-gateway.yaml

# Get ingress IP
kubectl get svc istio-ingressgateway -n istio-system
```

## AWS EKS Deployment

### Step 1: Create EKS Cluster with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Configure kubectl
aws eks update-kubeconfig --name service-mesh-observatory --region us-east-1
```

The Terraform configuration provisions:
- EKS cluster (v1.28) with managed node groups
- VPC with public/private subnets across 3 AZs
- NAT Gateway for private subnet internet access
- Security groups for cluster and worker nodes
- IAM roles for cluster and service accounts
- RDS PostgreSQL (TimescaleDB extension)
- ElastiCache Redis cluster
- S3 bucket for backups

### Step 2: Install Istio on EKS

```bash
# Install Istio
istioctl install --set profile=default \
  --set meshConfig.accessLogFile=/dev/stdout \
  --set meshConfig.outboundTrafficPolicy.mode=REGISTRY_ONLY \
  -y

# Enable sidecar injection
kubectl label namespace observatory istio-injection=enabled
```

### Step 3: Configure AWS-Specific Settings

```bash
# Create AWS load balancer controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=service-mesh-observatory

# Configure external DNS (optional)
helm install external-dns bitnami/external-dns \
  --set provider=aws \
  --set policy=sync \
  --set aws.region=us-east-1
```

### Step 4: Deploy with Production Overlay

```bash
# Update image tags in production overlay
cd infrastructure/kubernetes/overlays/production
kustomize edit set image \
  ghcr.io/ryanwelchtech/observatory-backend:v1.0.0 \
  ghcr.io/ryanwelchtech/observatory-frontend:v1.0.0

# Deploy to production
kubectl apply -k infrastructure/kubernetes/overlays/production/

# Verify deployment
kubectl get pods -n observatory
kubectl get hpa -n observatory
```

## Configuration

### Environment Variables

**Backend** (configured in ConfigMap):
```yaml
DATABASE_URL: postgresql://user:pass@rds-endpoint:5432/observatory
REDIS_URL: redis://elasticache-endpoint:6379/0
PROMETHEUS_URL: http://prometheus.monitoring:9090
JAEGER_ENDPOINT: http://jaeger.monitoring:16686
KUBERNETES_IN_CLUSTER: "True"
```

**Frontend** (configured in Deployment):
```yaml
NEXT_PUBLIC_API_URL: https://api.observatory.example.com
NEXT_PUBLIC_WS_URL: wss://api.observatory.example.com/ws
```

### Resource Limits

Adjust resource limits based on cluster size and traffic:

```yaml
# Small cluster (<50 services)
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi

# Medium cluster (50-200 services)
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi

# Large cluster (>200 services)
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

### HPA Configuration

Tune auto-scaling based on traffic patterns:

```yaml
# Conservative (stable traffic)
spec:
  minReplicas: 3
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80

# Aggressive (spiky traffic)
spec:
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

## Verification

### Health Checks

```bash
# Backend health
kubectl exec -it deployment/observatory-backend -n observatory -- \
  curl http://localhost:8000/health

# Frontend health
kubectl exec -it deployment/observatory-frontend -n observatory -- \
  curl http://localhost:3000/

# Database connectivity
kubectl exec -it deployment/observatory-backend -n observatory -- \
  curl http://localhost:8000/ready
```

### Integration Tests

```bash
# Test Prometheus connectivity
kubectl exec -it deployment/observatory-backend -n observatory -- \
  python -c "import requests; print(requests.get('http://prometheus.monitoring:9090/-/healthy').status_code)"

# Test Kubernetes API access
kubectl exec -it deployment/observatory-backend -n observatory -- \
  python -c "from kubernetes import client, config; config.load_incluster_config(); v1=client.CoreV1Api(); print(len(v1.list_namespace().items))"

# Test Redis connectivity
kubectl exec -it deployment/observatory-backend -n observatory -- \
  python -c "import redis; r=redis.from_url('redis://redis:6379/0'); r.ping()"
```

### Access Application

```bash
# Port-forward (development)
kubectl port-forward svc/observatory-frontend 3000:3000 -n observatory

# Access via ingress (production)
# https://observatory.example.com
```

## Troubleshooting

### Backend Pod Crash Loop

```bash
# Check logs
kubectl logs -l app=observatory-backend -n observatory --tail=100

# Common issues:
# 1. Database connection failure
kubectl exec -it deployment/observatory-backend -n observatory -- env | grep DATABASE

# 2. Missing RBAC permissions
kubectl get clusterrolebinding observatory-backend-reader

# 3. Insufficient resources
kubectl describe pod -l app=observatory-backend -n observatory | grep -A 5 Events
```

### Prometheus Scraping Issues

```bash
# Verify Prometheus configuration
kubectl get configmap prometheus-config -n monitoring -o yaml

# Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Visit http://localhost:9090/targets

# Verify pod annotations
kubectl get pod -l app=observatory-backend -n observatory -o yaml | grep prometheus.io
```

### WebSocket Connection Failures

```bash
# Check ingress WebSocket support
kubectl get gateway observatory-gateway -n observatory -o yaml

# Verify backend WebSocket endpoint
kubectl exec -it deployment/observatory-backend -n observatory -- \
  curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/ws

# Check network policies
kubectl get networkpolicy -n observatory
```

### Istio Sidecar Injection Not Working

```bash
# Verify namespace label
kubectl get namespace observatory --show-labels

# Check Istio mutating webhook
kubectl get mutatingwebhookconfigurations | grep istio

# Restart pods to trigger injection
kubectl rollout restart deployment/observatory-backend -n observatory
```

### High Memory Usage

```bash
# Check memory consumption
kubectl top pods -n observatory

# Adjust limits if needed
kubectl set resources deployment observatory-backend \
  --limits=memory=2Gi \
  --requests=memory=1Gi \
  -n observatory

# Check for memory leaks
kubectl exec -it deployment/observatory-backend -n observatory -- \
  python -c "import gc; gc.collect(); print('Garbage collected')"
```

## Rollback Procedures

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/observatory-backend -n observatory

# Rollback to previous version
kubectl rollout undo deployment/observatory-backend -n observatory

# Rollback to specific revision
kubectl rollout undo deployment/observatory-backend --to-revision=3 -n observatory
```

### Database Rollback

```bash
# Restore from S3 backup
aws s3 cp s3://observatory-backups/timescaledb-2024-12-29.dump /tmp/

# Restore to database
kubectl exec -it timescaledb-0 -n observatory -- \
  pg_restore -U observatory -d observatory /tmp/timescaledb-2024-12-29.dump
```

## Maintenance

### Updating Application

```bash
# Update image tags
kubectl set image deployment/observatory-backend \
  backend=ghcr.io/ryanwelchtech/observatory-backend:v1.1.0 \
  -n observatory

# Monitor rollout
kubectl rollout status deployment/observatory-backend -n observatory
```

### Database Maintenance

```bash
# Vacuum database (reclaim space)
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "VACUUM ANALYZE;"

# Check database size
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "SELECT pg_size_pretty(pg_database_size('observatory'));"
```

### Certificate Rotation

Istio automatically rotates mTLS certificates every 90 days. To manually trigger rotation:

```bash
# Restart istiod to generate new certificates
kubectl rollout restart deployment/istiod -n istio-system

# Restart workloads to pick up new certificates
kubectl rollout restart deployment/observatory-backend -n observatory
kubectl rollout restart deployment/observatory-frontend -n observatory
```
