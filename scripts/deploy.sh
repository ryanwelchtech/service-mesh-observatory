#!/bin/bash
set -e

# Service Mesh Observatory Deployment Script
# Automates deployment to Kubernetes cluster

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m'

log_info() {
    echo -e "${COLOR_GREEN}[INFO]${COLOR_NC} $1"
}

log_warn() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_NC} $1"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl not found. Install from https://kubernetes.io/docs/tasks/tools/"; exit 1; }
    command -v kustomize >/dev/null 2>&1 || { log_error "kustomize not found. Install from https://kubectl.docs.kubernetes.io/installation/kustomize/"; exit 1; }

    log_info "Prerequisites check passed"
}

# Install Istio
install_istio() {
    log_info "Installing Istio..."

    if kubectl get namespace istio-system >/dev/null 2>&1; then
        log_warn "Istio already installed, skipping"
        return 0
    fi

    if ! command -v istioctl >/dev/null 2>&1; then
        log_error "istioctl not found. Install from https://istio.io/latest/docs/setup/getting-started/"
        exit 1
    fi

    istioctl install --set profile=demo -y
    kubectl label namespace default istio-injection=enabled --overwrite
    log_info "Istio installed successfully"
}

# Deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack..."

    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace monitoring istio-injection=enabled --overwrite

    # Deploy Prometheus
    if [ -f monitoring/prometheus/prometheus.yml ]; then
        kubectl create configmap prometheus-config \
            --from-file=prometheus.yml=monitoring/prometheus/prometheus.yml \
            --from-file=rules.yaml=monitoring/prometheus/rules.yaml \
            -n monitoring \
            --dry-run=client -o yaml | kubectl apply -f -
    fi

    log_info "Monitoring stack deployed"
}

# Create secrets
create_secrets() {
    log_info "Creating secrets..."

    if kubectl get secret observatory-secrets -n observatory >/dev/null 2>&1; then
        log_warn "Secrets already exist. Use 'kubectl delete secret observatory-secrets -n observatory' to recreate"
        return 0
    fi

    # Check if secrets.yaml exists
    if [ ! -f infrastructure/kubernetes/base/secrets.yaml ]; then
        log_error "secrets.yaml not found. Copy from secrets.yaml.example and update values"
        exit 1
    fi

    kubectl apply -f infrastructure/kubernetes/base/secrets.yaml
    log_info "Secrets created successfully"
}

# Deploy Observatory
deploy_observatory() {
    local ENVIRONMENT="${1:-base}"
    log_info "Deploying Observatory (environment: ${ENVIRONMENT})..."

    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl apply -k infrastructure/kubernetes/overlays/production/
    else
        kubectl apply -k infrastructure/kubernetes/base/
    fi

    log_info "Waiting for deployments to be ready..."
    kubectl rollout status deployment/observatory-backend -n observatory --timeout=5m
    kubectl rollout status deployment/observatory-frontend -n observatory --timeout=5m

    log_info "Observatory deployed successfully"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check pods
    BACKEND_READY=$(kubectl get deployment observatory-backend -n observatory -o jsonpath='{.status.readyReplicas}')
    FRONTEND_READY=$(kubectl get deployment observatory-frontend -n observatory -o jsonpath='{.status.readyReplicas}')

    if [ -z "$BACKEND_READY" ] || [ "$BACKEND_READY" -eq 0 ]; then
        log_error "Backend deployment not ready"
        kubectl logs -l app=observatory-backend -n observatory --tail=50
        exit 1
    fi

    if [ -z "$FRONTEND_READY" ] || [ "$FRONTEND_READY" -eq 0 ]; then
        log_error "Frontend deployment not ready"
        kubectl logs -l app=observatory-frontend -n observatory --tail=50
        exit 1
    fi

    # Test health endpoints
    log_info "Testing health endpoints..."
    kubectl run -it --rm curl-test --image=curlimages/curl --restart=Never -- \
        curl -f http://observatory-backend.observatory:8000/health || {
            log_error "Backend health check failed"
            exit 1
        }

    log_info "Deployment verification passed"
}

# Print access information
print_access_info() {
    log_info "======================================"
    log_info "Service Mesh Observatory Deployed!"
    log_info "======================================"
    echo ""
    log_info "Access the application:"
    echo ""
    echo "  kubectl port-forward svc/observatory-frontend 3000:3000 -n observatory"
    echo "  kubectl port-forward svc/observatory-backend 8000:8000 -n observatory"
    echo ""
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/api/docs"
    echo "  Metrics: http://localhost:8000/metrics"
    echo ""
    log_info "Monitoring:"
    echo ""
    echo "  kubectl port-forward svc/grafana 3001:3000 -n monitoring"
    echo "  kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
    echo ""
    echo "  Grafana: http://localhost:3001 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo ""
}

# Main execution
main() {
    local ENVIRONMENT="${1:-base}"

    log_info "Starting Service Mesh Observatory deployment..."

    check_prerequisites
    install_istio
    deploy_monitoring
    create_secrets
    deploy_observatory "$ENVIRONMENT"
    verify_deployment
    print_access_info

    log_info "Deployment complete!"
}

# Run main function
main "$@"
