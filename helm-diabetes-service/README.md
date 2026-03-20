# Helm Chart for Diabetes Service

This Helm chart automates the deployment of the Diabetes ML Service on Kubernetes.

## Quick Start

### Prerequisites
- Kubernetes 1.21+
- Helm 3.5+
- kubectl configured to your cluster

### Install Chart

```bash
# Using default values
helm install diabetes-service ./helm-diabetes-service

# With custom namespace
helm install diabetes-service ./helm-diabetes-service \
  --namespace ml-platform \
  --create-namespace

# With custom values
helm install diabetes-service ./helm-diabetes-service \
  -f custom-values.yaml
```

### Verify Installation

```bash
# Check release status
helm status diabetes-service

# List releases
helm list

# Check deployed resources
kubectl get all -l app=diabetes-service
```

## Configuration

### Main Values

| Setting | Default | Description |
|---------|---------|-------------|
| `replicaCount` | 2 | Number of deployment replicas |
| `image.repository` | your-registry/diabetes-service | Docker image repository |
| `image.tag` | latest | Docker image tag |
| `resources.requests.cpu` | 250m | CPU request |
| `resources.requests.memory` | 256Mi | Memory request |
| `resources.limits.cpu` | 500m | CPU limit |
| `resources.limits.memory` | 512Mi | Memory limit |

### Override Values

```bash
# Set specific values
helm install diabetes-service ./helm-diabetes-service \
  --set replicaCount=3 \
  --set image.tag=v1.2.0 \
  --set resources.limits.memory=1Gi

# Using custom values file
helm install diabetes-service ./helm-diabetes-service \
  -f custom-values.yaml \
  -f overrides.yaml
```

## Common Operations

### Upgrade Release

```bash
helm upgrade diabetes-service ./helm-diabetes-service
```

### Rollback Release

```bash
# List revisions
helm history diabetes-service

# Rollback to previous revision
helm rollback diabetes-service

# Rollback to specific revision
helm rollback diabetes-service 1
```

### Uninstall Release

```bash
helm uninstall diabetes-service

# Keep resources, just remove Helm release
helm uninstall diabetes-service --keep-history
```

### View Manifest

```bash
# See what will be deployed
helm template diabetes-service ./helm-diabetes-service

# With custom values
helm template diabetes-service ./helm-diabetes-service -f custom-values.yaml
```

## Advanced Configuration

### Enable Autoscaling

```bash
helm install diabetes-service ./helm-diabetes-service \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

### Custom Resource Limits

```bash
helm install diabetes-service ./helm-diabetes-service \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=512Mi \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi
```

### Custom Image Registry

```bash
helm install diabetes-service ./helm-diabetes-service \
  --set image.repository=myregistry.azurecr.io/diabetes-service \
  --set image.pullPolicy=Always
```

### Node Selection

```bash
helm install diabetes-service ./helm-diabetes-service \
  --set nodeSelector.disktype=ssd \
  --set nodeSelector.zone=us-west-1
```

## Chart Structure

```
helm-diabetes-service/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default configuration
├── charts/                     # Dependency charts (if any)
├── templates/
│   ├── _helpers.tpl           # Template helpers
│   ├── deployment.yaml        # Deployment spec
│   ├── service.yaml           # Service definition
│   ├── ingress.yaml           # Ingress configuration
│   ├── configmap.yaml         # ConfigMaps
│   ├── serviceaccount.yaml    # RBAC
│   ├── hpa.yaml               # Horizontal Pod Autoscaler
│   └── pdb.yaml               # Pod Disruption Budget
└── README.md                  # This file
```

## Template Files

### deployment.yaml
Kubernetes Deployment with:
- Container specification
- Environment variables
- Resource requests/limits
- Health probes (startup, readiness, liveness)
- Volume mounts
- Pod security context

### service.yaml
Kubernetes Service for:
- Internal service discovery
- ClusterIP exposure

### ingress.yaml
Ingress configuration for:
- HTTP routing
- TLS (optional)
- Rate limiting

### configmap.yaml
Configuration management for:
- Environment variables
- Configuration files (if needed)

### hpa.yaml
Horizontal Pod Autoscaler for:
- CPU-based scaling
- Memory-based scaling
- Custom metrics

## Troubleshooting

### Chart Validation

```bash
# Validate chart syntax
helm lint ./helm-diabetes-service

# Check for issues
helm template diabetes-service ./helm-diabetes-service --debug
```

### View Rendered Templates

```bash
# See all rendered manifests
helm template diabetes-service ./helm-diabetes-service

# See specific template
helm template diabetes-service ./helm-diabetes-service \
  --show-only templates/deployment.yaml
```

### Common Issues

**Issue**: Pod won't start
```bash
# Check events
kubectl describe pod -l app=diabetes-service

# Check logs
kubectl logs -l app=diabetes-service
```

**Issue**: ImagePullBackOff
```bash
# Verify image exists in registry
# Update image.repository in values.yaml
helm upgrade diabetes-service ./helm-diabetes-service \
  --set image.repository=correct-registry/image
```

**Issue**: CrashLoopBackOff
```bash
# Check application logs
kubectl logs -l app=diabetes-service --previous

# Verify environment variables
kubectl env pods -l app=diabetes-service
```

## Production Considerations

### Security
- Use ImagePullSecrets for private registries
- Enable Pod Security Policies
- Set SecurityContexts
- Use NetworkPolicies

### Performance
- Configure resource requests/limits appropriately
- Enable HPA for scaling
- Use local storage for ephemeral data
- Consider node affinity rules

### Reliability
- Set appropriate probes (startup, readiness, liveness)
- Use PodDisruptionBudgets
- Configure pod anti-affinity
- Use multiple replicas

### Monitoring
- Enable Prometheus scraping
- Configure dashboards in Grafana
- Set up alerts

## Examples

### Production Deployment

```bash
helm install diabetes-service ./helm-diabetes-service \
  --namespace ml-platform \
  --values production-values.yaml \
  --wait \
  --timeout 5m
```

### With MLflow Integration

The chart includes environment variables for MLflow:
```yaml
env:
  MLFLOW_TRACKING_URI: "http://mlflow-service.ml-platform.svc.cluster.local:5000"
  MODEL_VERSION: "2"
```

### Persistent Data

Configure volumes in values.yaml:
```yaml
volumes:
  - name: models
    persistentVolumeClaim:
      claimName: models-pvc
```

## Help

For more information:
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## Support

For issues specific to this chart, check:
- [GitHub Issues](../issues)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
