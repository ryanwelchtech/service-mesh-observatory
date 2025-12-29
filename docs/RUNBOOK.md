# Operations Runbook

Operational procedures and troubleshooting guide for Service Mesh Observatory.

## Table of Contents
- [Daily Operations](#daily-operations)
- [Monitoring](#monitoring)
- [Common Issues](#common-issues)
- [Emergency Procedures](#emergency-procedures)
- [Maintenance Windows](#maintenance-windows)

## Daily Operations

### Health Check Routine

**Morning Checklist** (15 minutes):

```bash
# 1. Check all pods are running
kubectl get pods -n observatory
kubectl get pods -n monitoring

# 2. Verify HPA status
kubectl get hpa -n observatory

# 3. Check recent alerts
kubectl logs -l app=observatory-backend -n observatory --since=24h | grep ERROR

# 4. Verify dashboard accessibility
curl -f https://observatory.example.com/health || echo "Frontend unreachable"

# 5. Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
```

Expected output: All services running, no critical errors, all Prometheus targets up

### Metrics Review

**Key Metrics to Monitor**:

1. **Request Rate**
   ```promql
   sum(rate(istio_requests_total[5m]))
   ```
   Threshold: Should match expected traffic (baseline ±20%)

2. **Error Rate**
   ```promql
   sum(rate(istio_requests_total{response_code=~"5.."}[5m])) / sum(rate(istio_requests_total[5m])) * 100
   ```
   Threshold: <1% (alert if >5%)

3. **P95 Latency**
   ```promql
   histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))
   ```
   Threshold: <200ms (alert if >500ms)

4. **Certificate Health**
   ```promql
   observatory_mtls_certificates_expiring_7d
   ```
   Threshold: 0 (alert if >0)

5. **Anomaly Rate**
   ```promql
   rate(observatory_anomaly_detections_total[1h])
   ```
   Threshold: <0.1/s (investigate if >1/s)

## Monitoring

### Grafana Dashboards

**Service Mesh Overview**:
- URL: `http://grafana.monitoring:3000/d/observatory-overview`
- Panels: Request rate, error rate, latency, topology
- Refresh: 10s

**Certificate Health**:
- URL: `http://grafana.monitoring:3000/d/observatory-certs`
- Panels: Expiring certificates, health score
- Refresh: 5m

**Anomaly Detection**:
- URL: `http://grafana.monitoring:3000/d/observatory-anomalies`
- Panels: Anomaly timeline, top anomalous services
- Refresh: 30s

### Alert Routing

**Severity Levels**:
- **Critical**: PagerDuty (immediate), Slack #incidents
- **High**: Slack #alerts, Email ops team
- **Medium**: Slack #monitoring
- **Low**: Email weekly digest

**On-Call Rotation**:
- Primary: Senior SRE
- Secondary: Platform Engineer
- Escalation: Engineering Manager

## Common Issues

### Issue 1: Backend Pod CrashLoopBackOff

**Symptoms**:
```bash
$ kubectl get pods -n observatory
NAME                                   READY   STATUS             RESTARTS
observatory-backend-5d8f7c9-xyz        0/2     CrashLoopBackOff   5
```

**Root Causes**:
1. Database connection failure
2. Missing environment variables
3. Out of memory (OOMKilled)

**Diagnosis**:
```bash
# Check pod logs
kubectl logs observatory-backend-5d8f7c9-xyz -c backend -n observatory

# Check previous logs (if restarted)
kubectl logs observatory-backend-5d8f7c9-xyz -c backend -n observatory --previous

# Check pod events
kubectl describe pod observatory-backend-5d8f7c9-xyz -n observatory
```

**Resolution**:

**If database connection error**:
```bash
# Verify database secret
kubectl get secret observatory-secrets -n observatory -o yaml

# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql postgresql://user:pass@timescaledb:5432/observatory
```

**If missing env vars**:
```bash
# Check configmap
kubectl get configmap observatory-config -n observatory -o yaml

# Restart deployment
kubectl rollout restart deployment/observatory-backend -n observatory
```

**If OOMKilled**:
```bash
# Increase memory limit
kubectl set resources deployment observatory-backend \
  --limits=memory=2Gi \
  --requests=memory=1Gi \
  -n observatory
```

### Issue 2: High Latency (P95 >500ms)

**Symptoms**:
- Grafana dashboard shows P95 latency spike
- Users report slow page loads

**Diagnosis**:
```bash
# Identify slow services
kubectl exec deployment/observatory-backend -n observatory -- \
  curl -s http://prometheus.monitoring:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le, destination_service_name))' | \
  jq '.data.result'

# Check database query performance
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Resolution**:

**If database slow queries**:
```bash
# Add missing indexes
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);"

# Vacuum database
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "VACUUM ANALYZE;"
```

**If backend overload**:
```bash
# Scale up replicas
kubectl scale deployment observatory-backend --replicas=10 -n observatory

# Wait for HPA to stabilize
kubectl get hpa -n observatory --watch
```

**If network issues**:
```bash
# Check Envoy proxy stats
kubectl exec deployment/observatory-backend -c istio-proxy -n observatory -- \
  curl -s http://localhost:15000/stats/prometheus | grep upstream_rq_time
```

### Issue 3: Certificate Expiring Soon

**Symptoms**:
- Alert: "CertificateExpiringIn7Days"
- Dashboard shows certificates with <7 days validity

**Diagnosis**:
```bash
# List expiring certificates
kubectl exec deployment/observatory-backend -n observatory -- \
  curl -s http://localhost:8000/api/v1/certificates/expiring?days=7
```

**Resolution**:

**Trigger Istio certificate rotation**:
```bash
# Restart istiod to force cert regeneration
kubectl rollout restart deployment/istiod -n istio-system

# Restart workloads to pick up new certs
kubectl rollout restart deployment/observatory-backend -n observatory
kubectl rollout restart deployment/observatory-frontend -n observatory

# Verify new certificate expiration
kubectl exec deployment/observatory-backend -n observatory -c istio-proxy -- \
  openssl s_client -showcerts -connect observatory-backend:8000 2>/dev/null | \
  openssl x509 -noout -dates
```

### Issue 4: Anomaly False Positives

**Symptoms**:
- High rate of anomaly alerts
- No actual security incidents

**Diagnosis**:
```bash
# Review recent anomalies
kubectl exec deployment/observatory-backend -n observatory -- \
  curl -s http://localhost:8000/api/v1/anomalies?limit=50

# Check anomaly score distribution
kubectl logs -l app=observatory-backend -n observatory | grep anomaly_score
```

**Resolution**:

**Adjust anomaly threshold**:
```bash
# Edit configmap
kubectl edit configmap observatory-config -n observatory

# Change ANOMALY_DETECTION_THRESHOLD from 0.85 to 0.90
# Restart backend
kubectl rollout restart deployment/observatory-backend -n observatory
```

**Retrain baseline model**:
```bash
# Collect last 7 days of metrics as new baseline
kubectl exec deployment/observatory-backend -n observatory -- \
  python -m app.services.anomaly_service --retrain-baseline
```

### Issue 5: Prometheus High Cardinality

**Symptoms**:
- Prometheus pod OOMKilled
- Slow queries in Grafana

**Diagnosis**:
```bash
# Check cardinality
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
curl http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName | sort_by(.value) | reverse | .[:10]'

# Check memory usage
kubectl top pod -n monitoring
```

**Resolution**:

**Drop high-cardinality labels**:
```yaml
# Edit prometheus.yml
metric_relabel_configs:
- source_labels: [__name__]
  regex: 'istio_request_bytes_bucket.*'
  action: drop
- source_labels: [response_code]
  regex: '.*'
  target_label: response_code
  replacement: '${1}xx'
```

**Increase retention compression**:
```bash
# Edit Prometheus StatefulSet
kubectl edit statefulset prometheus -n monitoring

# Add args:
--storage.tsdb.retention.time=7d
--storage.tsdb.min-block-duration=2h
--storage.tsdb.max-block-duration=24h
```

## Emergency Procedures

### Complete Service Outage

**Severity**: Critical
**Response Time**: Immediate

**Steps**:

1. **Acknowledge incident** (1 minute)
   ```bash
   # Post to Slack #incidents
   "@here INCIDENT: Observatory complete outage. Investigating."
   ```

2. **Assess impact** (2 minutes)
   ```bash
   # Check all pods
   kubectl get pods -n observatory
   kubectl get pods -n monitoring

   # Check ingress
   kubectl get ingress -n observatory
   ```

3. **Emergency rollback** (5 minutes)
   ```bash
   # Rollback to previous version
   kubectl rollout undo deployment/observatory-backend -n observatory
   kubectl rollout undo deployment/observatory-frontend -n observatory

   # Verify rollback
   kubectl rollout status deployment/observatory-backend -n observatory
   ```

4. **If rollback fails, restore from backup** (15 minutes)
   ```bash
   # Delete corrupted deployment
   kubectl delete namespace observatory

   # Restore from git
   git checkout tags/v1.0.0
   kubectl apply -k infrastructure/kubernetes/base/

   # Restore database
   kubectl exec -it timescaledb-0 -n observatory -- \
     pg_restore -U observatory -d observatory /backups/latest.dump
   ```

5. **Verify recovery** (5 minutes)
   ```bash
   # Test health endpoints
   curl -f https://observatory.example.com/health

   # Check metrics
   curl -f https://observatory.example.com/api/v1/metrics/overview

   # Update incident channel
   "@here RESOLVED: Observatory restored. Investigating root cause."
   ```

### Database Corruption

**Severity**: Critical
**Response Time**: <15 minutes

**Steps**:

```bash
# 1. Isolate database
kubectl scale deployment observatory-backend --replicas=0 -n observatory

# 2. Verify corruption
kubectl exec -it timescaledb-0 -n observatory -- \
  psql -U observatory -c "SELECT pg_database.datname, pg_database_size(pg_database.datname) FROM pg_database;"

# 3. Restore from latest backup
aws s3 cp s3://observatory-backups/timescaledb-latest.dump /tmp/

kubectl exec -it timescaledb-0 -n observatory -- \
  dropdb -U observatory observatory

kubectl exec -it timescaledb-0 -n observatory -- \
  createdb -U observatory observatory

kubectl cp /tmp/timescaledb-latest.dump \
  observatory/timescaledb-0:/tmp/restore.dump

kubectl exec -it timescaledb-0 -n observatory -- \
  pg_restore -U observatory -d observatory /tmp/restore.dump

# 4. Restart backend
kubectl scale deployment observatory-backend --replicas=3 -n observatory
```

## Maintenance Windows

### Planned Upgrade Procedure

**Timing**: Saturday 02:00-04:00 UTC (low traffic)
**Communication**: 7 days advance notice

**Pre-Maintenance** (Friday before):
```bash
# 1. Create full backup
kubectl exec timescaledb-0 -n observatory -- \
  pg_dump -U observatory -F c -b -v -f /backups/pre-upgrade-$(date +%Y%m%d).dump observatory

# 2. Upload backup to S3
kubectl cp observatory/timescaledb-0:/backups/pre-upgrade-*.dump /tmp/
aws s3 cp /tmp/pre-upgrade-*.dump s3://observatory-backups/

# 3. Test rollback procedure in staging
kubectl config use-context staging
kubectl rollout undo deployment/observatory-backend -n observatory
# Verify, then roll forward again
```

**During Maintenance**:
```bash
# 1. Enable maintenance mode
kubectl scale deployment observatory-frontend --replicas=1 -n observatory
# Deploy maintenance page

# 2. Drain traffic
kubectl annotate deployment observatory-backend \
  maintenance="true" -n observatory

# 3. Apply updates
kubectl set image deployment/observatory-backend \
  backend=ghcr.io/ryanwelchtech/observatory-backend:v1.1.0 -n observatory

kubectl rollout status deployment/observatory-backend -n observatory

# 4. Run database migrations
kubectl exec deployment/observatory-backend -n observatory -- \
  alembic upgrade head

# 5. Smoke test
curl -f https://observatory.example.com/api/v1/metrics/overview

# 6. Restore traffic
kubectl scale deployment observatory-frontend --replicas=3 -n observatory
kubectl annotate deployment observatory-backend maintenance- -n observatory
```

**Post-Maintenance**:
```bash
# Monitor for 30 minutes
kubectl logs -f deployment/observatory-backend -n observatory | grep ERROR

# Check metrics
kubectl exec deployment/observatory-backend -n observatory -- \
  curl http://localhost:8000/metrics | grep observatory_

# Verify anomaly detection
kubectl exec deployment/observatory-backend -n observatory -- \
  curl http://localhost:8000/api/v1/anomalies | jq '.'

# Send all-clear notification
# Post to Slack: "Maintenance complete. All systems operational."
```

### Database Maintenance

**Weekly** (Sunday 03:00 UTC):
```bash
# Vacuum and analyze
kubectl exec timescaledb-0 -n observatory -- \
  psql -U observatory -c "VACUUM ANALYZE;"

# Reindex
kubectl exec timescaledb-0 -n observatory -- \
  psql -U observatory -c "REINDEX DATABASE observatory;"
```

**Monthly** (First Sunday 03:00 UTC):
```bash
# Update statistics
kubectl exec timescaledb-0 -n observatory -- \
  psql -U observatory -c "ANALYZE VERBOSE;"

# Check for bloat
kubectl exec timescaledb-0 -n observatory -- \
  psql -U observatory -c "
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;
  "
```

## Performance Tuning

### Backend Optimization

**Increase worker threads** (for CPU-bound workloads):
```bash
kubectl set env deployment/observatory-backend \
  UVICORN_WORKERS=4 \
  -n observatory
```

**Tune connection pool**:
```bash
kubectl set env deployment/observatory-backend \
  DB_POOL_SIZE=30 \
  DB_MAX_OVERFLOW=20 \
  -n observatory
```

### Database Optimization

**Tune PostgreSQL settings**:
```bash
kubectl exec timescaledb-0 -n observatory -- \
  psql -U observatory -c "
    ALTER SYSTEM SET shared_buffers = '4GB';
    ALTER SYSTEM SET effective_cache_size = '12GB';
    ALTER SYSTEM SET work_mem = '64MB';
    ALTER SYSTEM SET maintenance_work_mem = '1GB';
  "

# Restart database
kubectl delete pod timescaledb-0 -n observatory
```

### Prometheus Optimization

**Reduce retention**:
```bash
kubectl edit statefulset prometheus -n monitoring
# Change: --storage.tsdb.retention.time=7d
```

**Increase scrape interval**:
```bash
kubectl edit configmap prometheus-config -n monitoring
# Change: scrape_interval: 30s (from 15s)
```
