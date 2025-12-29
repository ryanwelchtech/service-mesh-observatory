#!/bin/bash
set -e

# Service Mesh Observatory Cleanup Script
# Safely removes all Observatory resources from Kubernetes

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

# Confirm cleanup
confirm_cleanup() {
    log_warn "This will delete all Observatory resources from the cluster"
    echo ""
    kubectl get pods -n observatory 2>/dev/null || true
    echo ""

    read -p "Are you sure you want to proceed? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_info "Cleanup cancelled"
        exit 0
    fi
}

# Delete Observatory namespace
delete_observatory() {
    log_info "Deleting Observatory namespace..."

    if ! kubectl get namespace observatory >/dev/null 2>&1; then
        log_warn "Observatory namespace not found, skipping"
        return 0
    fi

    kubectl delete namespace observatory --timeout=5m
    log_info "Observatory namespace deleted"
}

# Delete monitoring namespace
delete_monitoring() {
    read -p "Delete monitoring namespace? (yes/no): " DELETE_MONITORING
    if [ "$DELETE_MONITORING" = "yes" ]; then
        log_info "Deleting monitoring namespace..."
        kubectl delete namespace monitoring --timeout=5m
        log_info "Monitoring namespace deleted"
    else
        log_info "Skipping monitoring namespace deletion"
    fi
}

# Delete Istio
delete_istio() {
    read -p "Delete Istio? (yes/no): " DELETE_ISTIO
    if [ "$DELETE_ISTIO" = "yes" ]; then
        log_info "Deleting Istio..."
        if command -v istioctl >/dev/null 2>&1; then
            istioctl uninstall --purge -y
            kubectl delete namespace istio-system --timeout=5m
            log_info "Istio deleted"
        else
            log_warn "istioctl not found, manually delete istio-system namespace"
        fi
    else
        log_info "Skipping Istio deletion"
    fi
}

# Delete PVCs
delete_pvcs() {
    log_info "Checking for persistent volume claims..."

    PVCS=$(kubectl get pvc -n observatory -o name 2>/dev/null || true)
    if [ -n "$PVCS" ]; then
        log_warn "Found PVCs in observatory namespace:"
        kubectl get pvc -n observatory
        read -p "Delete these PVCs? This will delete all data! (yes/no): " DELETE_PVCS
        if [ "$DELETE_PVCS" = "yes" ]; then
            kubectl delete pvc --all -n observatory
            log_info "PVCs deleted"
        fi
    fi
}

# Clean up Docker resources (optional)
cleanup_docker() {
    read -p "Clean up Docker resources (containers, images, volumes)? (yes/no): " CLEANUP_DOCKER
    if [ "$CLEANUP_DOCKER" = "yes" ]; then
        log_info "Cleaning up Docker resources..."

        if command -v docker >/dev/null 2>&1; then
            # Stop and remove containers
            docker-compose down -v --remove-orphans 2>/dev/null || true

            # Remove images
            docker images | grep observatory | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

            # Clean up volumes
            docker volume ls | grep observatory | awk '{print $2}' | xargs -r docker volume rm 2>/dev/null || true

            log_info "Docker resources cleaned up"
        else
            log_warn "Docker not found, skipping Docker cleanup"
        fi
    fi
}

# Main execution
main() {
    log_info "Starting Service Mesh Observatory cleanup..."

    confirm_cleanup
    delete_pvcs
    delete_observatory
    delete_monitoring
    delete_istio
    cleanup_docker

    log_info "Cleanup complete!"
    log_info "All Observatory resources have been removed"
}

# Run main function
main "$@"
