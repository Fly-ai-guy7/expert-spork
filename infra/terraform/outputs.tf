# These outputs become the secrets your Helm chart consumes via External
# Secrets / sealed-secrets. They are commented out until you wire the actual
# cloud modules above.

# output "database_url" {
#   description = "Plug into the equalise-secrets Kubernetes Secret as DATABASE_URL"
#   value       = "postgresql+psycopg://${module.postgres.db_username}:${var.postgres_password}@${module.postgres.db_instance_address}:5432/${module.postgres.db_instance_name}"
#   sensitive   = true
# }
#
# output "celery_broker_url" {
#   description = "Plug into the equalise-secrets Kubernetes Secret as CELERY_BROKER_URL"
#   value       = "redis://${module.redis.endpoint}:6379/0"
# }
#
# output "celery_result_backend" {
#   value = "redis://${module.redis.endpoint}:6379/1"
# }
#
# output "backup_s3_bucket" {
#   value = aws_s3_bucket.backups.bucket
# }
