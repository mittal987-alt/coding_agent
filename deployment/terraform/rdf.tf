##############################################################
# KMS Key for RDS Encryption
##############################################################

resource "aws_kms_key" "rds" {

  description = "KMS Key for PostgreSQL Encryption"

  enable_key_rotation = true

  deletion_window_in_days = 30

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-rds-kms"
    }
  )
}

resource "aws_kms_alias" "rds" {

  name = "alias/${var.project_name}-rds"

  target_key_id = aws_kms_key.rds.key_id
}

##############################################################
# PostgreSQL Parameter Group
##############################################################

resource "aws_db_parameter_group" "postgres" {

  name   = "${var.project_name}-postgres"

  family = "postgres16"

  description = "Production PostgreSQL Parameter Group"

  parameter {

    name  = "log_statement"

    value = "ddl"
  }

  parameter {

    name  = "log_connections"

    value = "1"
  }

  parameter {

    name  = "log_disconnections"

    value = "1"
  }

  parameter {

    name  = "shared_preload_libraries"

    value = "pg_stat_statements"
  }

  parameter {

    name  = "log_min_duration_statement"

    value = "1000"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-postgres-params"
    }
  )
}

##############################################################
# Enhanced Monitoring IAM Role
##############################################################

resource "aws_iam_role" "rds_monitoring" {

  name = "${var.project_name}-rds-monitoring-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "monitoring.rds.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {

  role = aws_iam_role.rds_monitoring.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

##############################################################
# PostgreSQL RDS Instance
##############################################################

resource "aws_db_instance" "postgres" {

  identifier = "${var.project_name}-postgres"

  engine = "postgres"

  engine_version = var.db_engine_version

  instance_class = var.db_instance_class

  allocated_storage = var.db_allocated_storage

  max_allocated_storage = var.db_max_allocated_storage

  storage_type = "gp3"

  storage_encrypted = true

  kms_key_id = aws_kms_key.rds.arn

  db_name = var.db_name

  username = var.db_username

  password = var.db_password

  port = 5432

  db_subnet_group_name = aws_db_subnet_group.main.name

  vpc_security_group_ids = [
    aws_security_group.postgres.id
  ]

  parameter_group_name = aws_db_parameter_group.postgres.name

  multi_az = var.db_multi_az

  publicly_accessible = false

  deletion_protection = var.enable_deletion_protection

  backup_retention_period = var.db_backup_retention_period

  backup_window = var.db_backup_window

  maintenance_window = var.db_maintenance_window

  monitoring_interval = 60

  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  performance_insights_enabled = true

  performance_insights_kms_key_id = aws_kms_key.rds.arn

  enabled_cloudwatch_logs_exports = [
    "postgresql"
  ]

  skip_final_snapshot = false

  final_snapshot_identifier = "${var.project_name}-final-snapshot"

  apply_immediately = false

  auto_minor_version_upgrade = true

  copy_tags_to_snapshot = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-postgres"
    }
  )
}
##############################################################
# KMS Key for Redis Encryption
##############################################################

resource "aws_kms_key" "redis" {

  description = "KMS key for ElastiCache Redis encryption"

  enable_key_rotation = true

  deletion_window_in_days = 30

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-kms"
    }
  )
}

resource "aws_kms_alias" "redis" {

  name = "alias/${var.project_name}-redis"

  target_key_id = aws_kms_key.redis.key_id
}

##############################################################
# ElastiCache Subnet Group
##############################################################

resource "aws_elasticache_subnet_group" "redis" {

  name = "${var.project_name}-redis-subnet-group"

  subnet_ids = aws_subnet.private[*].id

  description = "Subnet group for Redis"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-subnet-group"
    }
  )
}

##############################################################
# Redis Parameter Group
##############################################################

resource "aws_elasticache_parameter_group" "redis" {

  name   = "${var.project_name}-redis-params"

  family = "redis7"

  description = "Production Redis Parameter Group"

  parameter {

    name  = "maxmemory-policy"

    value = "allkeys-lru"
  }

  parameter {

    name  = "timeout"

    value = "0"
  }

  parameter {

    name  = "tcp-keepalive"

    value = "300"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-params"
    }
  )
}

##############################################################
# Random Authentication Token
##############################################################

resource "random_password" "redis_auth" {

  length = 32

  special = true

  override_special = "!@#$%^&*()-_=+"
}

##############################################################
# Redis Replication Group
##############################################################

resource "aws_elasticache_replication_group" "redis" {

  replication_group_id = "${var.project_name}-redis"

  description = "Production Redis Replication Group"

  engine = "redis"

  engine_version = var.redis_engine_version

  node_type = var.redis_node_type

  parameter_group_name = aws_elasticache_parameter_group.redis.name

  subnet_group_name = aws_elasticache_subnet_group.redis.name

  security_group_ids = [
    aws_security_group.redis.id
  ]

  num_cache_clusters = var.redis_num_cache_clusters

  automatic_failover_enabled = true

  multi_az_enabled = true

  at_rest_encryption_enabled = true

  transit_encryption_enabled = true

  kms_key_id = aws_kms_key.redis.arn

  auth_token = random_password.redis_auth.result

  port = 6379

  maintenance_window = "sun:04:00-sun:05:00"

  snapshot_retention_limit = 7

  snapshot_window = "03:00-04:00"

  auto_minor_version_upgrade = true

  apply_immediately = false

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis"
    }
  )
}