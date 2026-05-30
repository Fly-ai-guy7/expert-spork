terraform {
  required_version = ">= 1.6"
  required_providers {
    # Pick one and uncomment in your real config:
    # aws    = { source = "hashicorp/aws",    version = "~> 5.0" }
    # google = { source = "hashicorp/google", version = "~> 5.0" }
  }

  # Use a remote backend in real environments (S3 + DynamoDB lock, or GCS, or Terraform Cloud).
  # backend "s3" {
  #   bucket         = "equalise-tfstate"
  #   key            = "envs/${var.env}/terraform.tfstate"
  #   region         = "eu-west-1"
  #   dynamodb_table = "equalise-tflock"
  # }
}

locals {
  tags = {
    project = "equalise-egypt"
    env     = var.env
  }
}

# --- Managed Postgres ---------------------------------------------------------
# Replace with the official cloud module. Required outputs:
#   - postgres.connection_url (postgresql+psycopg://... including credentials)
# Example AWS RDS:
#   module "postgres" {
#     source              = "terraform-aws-modules/rds/aws"
#     identifier          = "equalise-${var.env}"
#     engine              = "postgres"
#     engine_version      = "16"
#     instance_class      = var.postgres_instance_class
#     allocated_storage   = var.postgres_storage_gb
#     db_name             = "equalise"
#     username            = "equalise"
#     password            = var.postgres_password
#     vpc_security_group_ids = [var.db_security_group_id]
#     subnet_ids          = var.private_subnet_ids
#     backup_retention_period = 14
#     deletion_protection = var.env == "prod"
#     tags                = local.tags
#   }

# --- Managed Redis ------------------------------------------------------------
# Replace with the official cloud module. Required outputs:
#   - redis.broker_url (redis://...)
# Example AWS ElastiCache:
#   module "redis" {
#     source             = "terraform-aws-modules/elasticache/aws"
#     cluster_id         = "equalise-${var.env}"
#     engine             = "redis"
#     engine_version     = "7.0"
#     node_type          = var.redis_node_type
#     security_group_ids = [var.redis_security_group_id]
#     subnet_ids         = var.private_subnet_ids
#     tags               = local.tags
#   }

# --- Backups bucket ----------------------------------------------------------
# Where the daily pg_dump sidecar writes its archives. Set BACKUP_S3_BUCKET in
# the cluster's secrets to this bucket's name.
#   resource "aws_s3_bucket" "backups" {
#     bucket = "equalise-${var.env}-backups"
#     tags   = local.tags
#   }
#   resource "aws_s3_bucket_versioning" "backups" {
#     bucket = aws_s3_bucket.backups.id
#     versioning_configuration { status = "Enabled" }
#   }
#   resource "aws_s3_bucket_lifecycle_configuration" "backups" {
#     bucket = aws_s3_bucket.backups.id
#     rule {
#       id     = "expire-old"
#       status = "Enabled"
#       expiration { days = 90 }
#     }
#   }
