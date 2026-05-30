# EQUALISE Egypt — Infra (Terraform)

Minimal IaC for the managed dependencies a production EQUALISE install
needs: a Postgres database, a Redis instance, and an S3-compatible bucket
for off-site backups.

## Structure

```
infra/terraform/
├── main.tf          # provider + module wiring
├── variables.tf     # inputs (region, env, sizes, secrets references)
├── outputs.tf       # connection strings consumed by the Helm chart's
│                    #   ExternalSecret / sealed-secret
└── envs/
    ├── staging.tfvars
    └── prod.tfvars
```

## What this scaffold does NOT include

- Actual cloud provider modules (RDS, ElastiCache, S3 / Cloud SQL,
  MemoryStore, GCS). Drop in the official modules for your target. The
  variables + outputs in this skeleton match what the Helm chart expects.
- VPC / networking. Production should put Postgres + Redis in a private
  subnet and the cluster in another, peered, with security groups locking
  database ingress to the cluster's node CIDR.
- DNS, ACM / cert-manager. Caddy handles edge TLS in our compose-only
  topology; a k8s deployment would typically use cert-manager + an
  Ingress, or a managed ALB / GCLB.
- Secret storage. We expect you to run External Secrets (AWS Secrets
  Manager / Vault) or sealed-secrets and reference the secret name in
  `values.yaml`.

## Apply

```bash
cd infra/terraform
terraform init
terraform plan  -var-file=envs/staging.tfvars
terraform apply -var-file=envs/staging.tfvars
```

This scaffold is **deliberately unverified** in the current environment
(no cloud creds, no terraform binary in the harness). Real apply requires
your provider creds and a remote state backend.
