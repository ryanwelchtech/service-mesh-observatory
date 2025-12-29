# Security Hardening Guide

Security best practices and compliance controls for Service Mesh Observatory.

## Table of Contents
- [Security Architecture](#security-architecture)
- [Zero Trust Implementation](#zero-trust-implementation)
- [NIST 800-53 Alignment](#nist-800-53-alignment)
- [Vulnerability Management](#vulnerability-management)
- [Incident Response](#incident-response)
- [Compliance](#compliance)

## Security Architecture

### Defense in Depth

Service Mesh Observatory implements multiple security layers:

1. **Network Layer**: Kubernetes NetworkPolicy + Istio traffic rules
2. **Transport Layer**: mTLS encryption for all service-to-service communication
3. **Application Layer**: JWT authentication, RBAC authorization
4. **Data Layer**: Encryption at rest, encrypted backups

### Threat Model

**Assets**:
- Service mesh telemetry data (metrics, traces, logs)
- User credentials and session tokens
- TLS certificates and private keys
- Database connection strings

**Threats**:
- Unauthorized access to observability data
- Man-in-the-middle attacks on service communication
- Data exfiltration via compromised pods
- Privilege escalation within Kubernetes cluster

**Mitigations**:
- Strict mTLS enforcement (no plaintext traffic)
- AuthorizationPolicy whitelisting (deny-by-default)
- Read-only filesystem for containers
- Network policies limiting egress traffic

## Zero Trust Implementation

### Principle: Never Trust, Always Verify

#### mTLS Enforcement

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: observatory
spec:
  mtls:
    mode: STRICT  # Reject all plaintext traffic
```

**Verification**:
```bash
# Check mTLS status
istioctl authn tls-check observatory-backend.observatory.svc.cluster.local

# Should show: mTLS: STRICT for all connections
```

#### Service-to-Service Authorization

```yaml
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
        principals:
        - "cluster.local/ns/observatory/sa/observatory-frontend"
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

**Key Principles**:
- Deny by default (no implicit allow)
- Explicit service account principals
- Method and path restrictions
- Separate policies per service

#### Network Segmentation

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: observatory-backend-netpol
spec:
  podSelector:
    matchLabels:
      app: observatory-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: observatory-frontend
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Prometheus only
```

### Certificate Management

**Istio CA**:
- Automatically issues X.509 certificates to workloads
- Certificate validity: 90 days
- Automatic rotation at 67.5 days (75% lifetime)
- Root CA stored in istiod

**Monitoring**:
```bash
# Check certificate expiration
kubectl exec deployment/observatory-backend -n observatory -c istio-proxy -- \
  openssl s_client -showcerts -connect observatory-backend:8000 2>/dev/null | \
  openssl x509 -noout -dates
```

**Alerts**:
- 7 days: Critical alert, manual rotation required
- 30 days: Warning alert, monitor rotation
- 60 days: Info alert, verify auto-rotation working

## NIST 800-53 Alignment

### Access Control (AC)

**AC-2: Account Management**
- Kubernetes RBAC for service account permissions
- JWT tokens with 30-minute expiration
- Audit logging of all authentication events

**AC-3: Access Enforcement**
- Istio AuthorizationPolicy for L7 access control
- Kubernetes NetworkPolicy for L3/L4 enforcement
- Read-only filesystem prevents unauthorized modifications

**AC-6: Least Privilege**
- Backend service account has read-only cluster access
- No write permissions to Kubernetes resources
- Scoped RBAC limited to necessary namespaces only

### Audit and Accountability (AU)

**AU-2: Audit Events**
```yaml
# All API requests logged with:
- Timestamp
- Source service account
- HTTP method and path
- Response status code
- Request duration
```

**AU-3: Content of Audit Records**
- Structured JSON logging (machine-parseable)
- Correlation IDs for distributed tracing
- PII redaction in logs (no passwords, tokens)

**AU-9: Protection of Audit Information**
- Logs stored in Loki (append-only)
- 30-day retention with immutable storage
- S3 backup with encryption at rest

### System and Communications Protection (SC)

**SC-8: Transmission Confidentiality**
- TLS 1.3 for all external connections
- mTLS for all internal service mesh traffic
- Cipher suites: ECDHE-ECDSA-AES256-GCM-SHA384

**SC-12: Cryptographic Key Management**
- Istio CA for service mesh certificates
- Kubernetes Secrets for sensitive configuration
- Integration with external KMS (AWS KMS, HashiCorp Vault)

**SC-28: Protection of Information at Rest**
- TimescaleDB encryption at rest (AES-256)
- Kubernetes etcd encryption (encryption-at-rest enabled)
- Backup encryption with AWS S3 SSE-KMS

## Vulnerability Management

### Container Image Scanning

**CI/CD Pipeline**:
```yaml
# GitHub Actions workflow
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    format: 'sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # Fail build on high/critical CVEs
```

**Scanning Frequency**:
- Every commit: Scan base images and dependencies
- Daily: Scheduled scan of running containers
- Post-CVE disclosure: Ad-hoc scan within 24 hours

**Remediation SLA**:
- Critical CVEs: 48 hours
- High CVEs: 7 days
- Medium CVEs: 30 days

### Dependency Management

**Python (Backend)**:
```bash
# Automated dependency updates
pip install pip-audit
pip-audit --desc --fix

# Check for known vulnerabilities
safety check --json
```

**Node.js (Frontend)**:
```bash
# Automated dependency updates
npm audit --production
npm audit fix

# Use Snyk for continuous monitoring
snyk test --all-projects
```

### Runtime Security

**Falco Rules** (optional):
```yaml
# Detect unauthorized process execution
- rule: Unauthorized Process in Container
  condition: spawned_process and container.name = "observatory-backend" and not proc.name in (python, uvicorn)
  output: "Unauthorized process detected (user=%user.name command=%proc.cmdline)"
  priority: CRITICAL
```

## Incident Response

### Detection

**Anomaly Alerts**:
- Anomaly score >0.85: Automated Slack notification
- Certificate expiring <7 days: PagerDuty alert
- Unauthorized access attempt: Security team email

**SIEM Integration**:
- Forward logs to Splunk/ELK
- Correlation rules for attack patterns
- Automated incident ticket creation

### Containment

**Immediate Actions**:
```bash
# Isolate compromised pod
kubectl label pod <pod-name> quarantine=true -n observatory

# Apply deny-all network policy
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-quarantine
spec:
  podSelector:
    matchLabels:
      quarantine: "true"
  policyTypes:
  - Ingress
  - Egress
EOF

# Revoke service account permissions
kubectl delete clusterrolebinding observatory-backend-reader
```

### Investigation

**Evidence Collection**:
```bash
# Collect pod logs
kubectl logs <pod-name> -n observatory --all-containers > evidence-logs.txt

# Collect network traffic (if Istio access logs enabled)
kubectl exec -it <pod-name> -c istio-proxy -- cat /var/log/envoy/access.log > evidence-traffic.log

# Collect pod specification
kubectl get pod <pod-name> -n observatory -o yaml > evidence-pod.yaml

# Collect Prometheus metrics snapshot
curl http://prometheus:9090/api/v1/query?query=up > evidence-metrics.json
```

### Eradication

```bash
# Delete compromised pod
kubectl delete pod <pod-name> -n observatory

# Rotate all credentials
kubectl delete secret observatory-secrets -n observatory
kubectl create secret generic observatory-secrets --from-literal=...

# Rebuild container image
docker build --no-cache -t observatory-backend:patched .
docker push observatory-backend:patched

# Update deployment
kubectl set image deployment/observatory-backend backend=observatory-backend:patched -n observatory
```

### Recovery

```bash
# Restore from known-good backup
kubectl apply -k infrastructure/kubernetes/base/

# Verify integrity
kubectl exec deployment/observatory-backend -- sha256sum /app/main.py

# Re-enable traffic
kubectl delete networkpolicy deny-all-quarantine -n observatory
```

## Compliance

### FedRAMP High Alignment

**Security Controls**:
- AC-2, AC-3, AC-6: Access control
- AU-2, AU-3, AU-9: Audit logging
- SC-8, SC-12, SC-28: Encryption
- SI-2, SI-3, SI-4: System monitoring

**Evidence Artifacts**:
- Kubernetes RBAC policies
- Istio AuthorizationPolicy configurations
- Network policy YAML files
- Prometheus alerting rules
- Audit log exports

### SOC 2 Type II

**Trust Service Criteria**:
- **Security**: mTLS, RBAC, network policies
- **Availability**: HPA, health probes, multi-AZ deployment
- **Processing Integrity**: Input validation, error handling
- **Confidentiality**: Encryption at rest and in transit
- **Privacy**: PII redaction, data retention policies

### CIS Kubernetes Benchmark

**Level 1 Controls**:
- 5.1.1: Ensure RBAC is enabled ✓
- 5.2.1: Ensure NetworkPolicy is enabled ✓
- 5.3.1: Ensure securityContext is set ✓
- 5.7.1: Ensure read-only root filesystem ✓

**Level 2 Controls**:
- 5.1.5: Ensure service account tokens are mounted only where necessary ✓
- 5.2.6: Ensure CNI plugin supports NetworkPolicy ✓

## Secrets Management Best Practices

### Development

```bash
# Use .env files (gitignored)
cp .env.example .env
# Edit .env with development credentials
```

### Staging/Production

**Option 1: Kubernetes Secrets**
```bash
kubectl create secret generic observatory-secrets \
  --from-literal=database-url='postgresql://user:pass@host/db' \
  --from-literal=secret-key='random-secret-key' \
  -n observatory
```

**Option 2: HashiCorp Vault**
```bash
# Store in Vault
vault kv put secret/observatory/prod database_url='...' secret_key='...'

# Use Vault Agent injector
kubectl annotate pod observatory-backend \
  vault.hashicorp.com/agent-inject='true' \
  vault.hashicorp.com/role='observatory'
```

**Option 3: AWS Secrets Manager**
```bash
# Store in Secrets Manager
aws secretsmanager create-secret \
  --name observatory/prod/database-url \
  --secret-string 'postgresql://...'

# Use External Secrets Operator
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: observatory-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: observatory-secrets
  data:
  - secretKey: database-url
    remoteRef:
      key: observatory/prod/database-url
EOF
```

## Security Checklist

Pre-deployment security verification:

- [ ] mTLS STRICT mode enabled
- [ ] AuthorizationPolicy applied to all services
- [ ] NetworkPolicy configured for ingress/egress
- [ ] Container images scanned (no critical CVEs)
- [ ] Non-root user in Dockerfiles
- [ ] Read-only root filesystem enabled
- [ ] Resource limits configured
- [ ] Secrets not hardcoded in manifests
- [ ] TLS certificates valid and not expiring soon
- [ ] Audit logging enabled
- [ ] Monitoring alerts configured
- [ ] Backup and restore tested
- [ ] Incident response plan documented
