env                     = "staging"
region                  = "eu-west-1"
postgres_instance_class = "db.t4g.small"
postgres_storage_gb     = 20
redis_node_type         = "cache.t4g.micro"
# postgres_password set via TF_VAR_postgres_password env var (do not commit)
