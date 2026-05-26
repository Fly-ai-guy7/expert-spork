# Kubernetes Manifests — Deferred

Production K8s deployment is deferred. Place manifests here when ready:

- `deployment.yaml` — backend + frontend Deployments
- `service.yaml` — ClusterIP / LoadBalancer services
- `ingress.yaml` — TLS termination, host routing
- `configmap.yaml` — non-secret config
- `secret.yaml` — ANTHROPIC_API_KEY, DEEPSEEK_API_KEY (use external secret manager in real deployments)
- `hpa.yaml` — autoscaling on CPU + queue depth

For local development use `docker-compose.yml` at the repo root.
