variable "env" {
  description = "Environment name (staging | prod)"
  type        = string
}

variable "region" {
  description = "Cloud region"
  type        = string
  default     = "eu-west-1"
}

variable "postgres_instance_class" {
  description = "RDS / Cloud SQL instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "postgres_storage_gb" {
  description = "Initial allocated storage for Postgres (GB)"
  type        = number
  default     = 50
}

variable "postgres_password" {
  description = "Postgres master password. Source from your secret manager — do not commit."
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache / MemoryStore node type"
  type        = string
  default     = "cache.t4g.small"
}

variable "private_subnet_ids" {
  description = "Subnet IDs for the data-plane (Postgres + Redis)"
  type        = list(string)
  default     = []
}

variable "db_security_group_id" {
  description = "Security group allowing the app cluster to reach Postgres"
  type        = string
  default     = ""
}

variable "redis_security_group_id" {
  description = "Security group allowing the app cluster to reach Redis"
  type        = string
  default     = ""
}
