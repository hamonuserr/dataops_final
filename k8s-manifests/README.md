# Kubernetes Manifests

This directory contains raw Kubernetes manifests for deploying the Diabetes ML Service on Kubernetes without Helm.

## Files

| File | Purpose |
|------|---------|
| `00-namespace.yaml` | Create `ml-platform` namespace |
| `diabetes-deployment.yaml` | Deployment with 2 replicas, probes, security context |
| `diabetes-rbac.yaml` | ServiceAccount, Role, RoleBinding |
| `diabetes-service.yaml` | ClusterIP Service for internal networking |
| `diabetes-ingress.yaml` | Ingress for external HTTP access |
| `diabetes-hpa.yaml` | Horizontal Pod Autoscaler (2-5 replicas) |
| `diabetes-pdb.yaml` | Pod Disruption Budget (minimum 1 pod) |
| `diabetes-configmap.yaml` | Configuration as ConfigMap |

## Quick Deploy

### Deploy All Resources

```bash
# Apply all manifests in order
kubectl apply -f k8s-manifests/

# Or apply individually
kubectl apply -f k8s-manifests/00-namespace.yaml
kubectl apply -f k8s-manifests/diabetes-rbac.yaml
kubectl apply -f k8s-manifests/diabetes-configmap.yaml
kubectl apply -f k8s-manifests/diabetes-deployment.yaml
kubectl apply -f k8s-manifests/diabetes-service.yaml
kubectl apply -f k8s-manifests/diabetes-ingress.yaml
kubectl apply -f k8s-manifests/diabetes-hpa.yaml
kubectl apply -f k8s-manifests/diabetes-pdb.yaml
```

### Verify Deployment

```bash
# Check namespace
kubectl get namespace ml-platform

# Check all resources
kubectl get all -n ml-platform

# Check pods
kubectl get pods -n ml-platform -w

# Check services
kubectl get svc -n ml-platform

# Check ingress
kubectl get ingress -n ml-platform
```

### View Detailed Status

```bash
# Describe deployment
kubectl describe deployment diabetes-service -n ml-platform

# Get pod events
kubectl describe pod -n ml-platform

# View logs
kubectl logs -l app=diabetes-service -n ml-platform

# Follow logs
kubectl logs -f -l app=diabetes-service -n ml-platform
```

## Access Service

### Port Forward (Development)

```bash
# Forward to local port
kubectl port-forward -n ml-platform svc/diabetes-service 8000:8000

# Now access http://localhost:8000
curl http://localhost:8000/health
```

### Via Ingress (Production)

The Ingress expects host `ml.local`:

```bash
# Add to /etc/hosts
echo "127.0.0.1 ml.local" >> /etc/hosts

# Access via Ingress
curl http://ml.local/api/v1/predict
```

### Direct Service Access (Within Cluster)

```bash
# From within a pod in the cluster
curl http://diabetes-service.ml-platform.svc.cluster.local:8000/health
```

## Common Operations

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment diabetes-service -n ml-platform --replicas=5

# Check HPA limits (max 5)
kubectl get hpa -n ml-platform
```

### Update Image

```bash
# Update image version
kubectl set image deployment/diabetes-service \
  -n ml-platform \
  diabetes-service=myregistry.azurecr.io/diabetes-service:v1.2.0

# Monitor rollout
kubectl rollout status deployment/diabetes-service -n ml-platform

# Check rollout history
kubectl rollout history deployment/diabetes-service -n ml-platform

# Rollback if needed
kubectl rollout undo deployment/diabetes-service -n ml-platform
```

### Update Configuration

```bash
# Edit deployment
kubectl edit deployment diabetes-service -n ml-platform

# Or patch specific field
kubectl patch deployment diabetes-service -n ml-platform \
  -p '{"spec": {"replicas": 3}}'
```

### Delete Resources

```bash
# Delete entire namespace (removes all resources)
kubectl delete namespace ml-platform

# Or delete specific resources
kubectl delete -f k8s-manifests/
```

## Probes

### Startup Probe
- Path: `/ready`
- Initial Delay: 10s
- Period: 5s
- Failure Threshold: 30
- Gives 2.5 minutes for the app to start

### Readiness Probe
- Path: `/health`
- Initial Delay: 5s
- Period: 10s
- Detects when app is ready to serve traffic

### Liveness Probe
- Path: `/health`
- Initial Delay: 15s
- Period: 20s
- Restarts pod if unhealthy

## Resource Management

### Requests
- CPU: 250m
- Memory: 256Mi

### Limits
- CPU: 500m
- Memory: 512Mi

### HPA Scaling
- Minimum Replicas: 2
- Maximum Replicas: 5
- CPU Threshold: 70%
- Memory Threshold: 80%

## Security

### Pod Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

### Container Security Context
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false
  capabilities:
    drop:
      - ALL
```

### RBAC
- ServiceAccount: `diabetes-service`
- Role: Limited to reading pods and configmaps
- Minimal privileges principle

## Networking

### Service
- Type: ClusterIP (internal only)
- Port: 8000
- Target Port: 8000

### Ingress
- Class: nginx
- Path: `/api/v1/predict`, `/health`, `/metrics`
- TLS: Optional (configure as needed)
- Rate Limiting: 10 requests per minute

## Persistence

### Volume Mounts
- `/app/logs` - EmptyDir (ephemeral)
- `/app/models` - EmptyDir (ephemeral)

For persistent storage, attach PersistentVolumeClaims (PVC).

## Monitoring

### Prometheus Annotations
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Available Metrics
- `diabetes_predictions_total`
- `diabetes_prediction_latency_seconds`
- `diabetes_active_requests`
- `mlflow_connection_status`

## Troubleshooting

### Pod Won't Start

```bash
# Check events and logs
kubectl describe pod <pod-name> -n ml-platform
kubectl logs <pod-name> -n ml-platform

# Check resource availability
kubectl top nodes
kubectl top pods -n ml-platform
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n ml-platform

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never \
  -- curl http://diabetes-service.ml-platform.svc.cluster.local:8000/health
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress diabetes-service -n ml-platform

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never \
  -- nslookup ml.local
```

## Production Checklist

- [ ] Verify all pods are running
- [ ] Test health endpoints
- [ ] Configure  monitoring/logging
- [ ] Set up alerting
- [ ] Test failover scenarios
- [ ] Configure backups
- [ ] Set resource limits/requests appropriately
- [ ] Enable security policies
- [ ] Configure image registry authentication
- [ ] Set up RBAC properly
- [ ] Enable audit logging
- [ ] Test disaster recovery

## More Information

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Helm Alternative](../helm-diabetes-service/)
