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
##############################################################
# CloudWatch Log Group
##############################################################

resource "aws_cloudwatch_log_group" "redis" {

  name = "/aws/elasticache/${aws_elasticache_replication_group.redis.replication_group_id}"

  retention_in_days = var.log_retention_days

  kms_key_id = aws_kms_key.redis.arn

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-logs"
    }
  )
}

##############################################################
# Redis Event Subscription
##############################################################

resource "aws_elasticache_event_subscription" "redis" {

  name = "${var.project_name}-redis-events"

  sns_topic_arn = aws_sns_topic.database_events.arn

  source_type = "replication-group"

  source_ids = [
    aws_elasticache_replication_group.redis.replication_group_id
  ]

  enabled = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-events"
    }
  )
}

##############################################################
# CPU Utilization Alarm
##############################################################

resource "aws_cloudwatch_metric_alarm" "redis_cpu" {

  alarm_name = "${var.project_name}-redis-high-cpu"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2

  metric_name = "CPUUtilization"

  namespace = "AWS/ElastiCache"

  period = 300

  statistic = "Average"

  threshold = 80

  alarm_description = "Redis CPU utilization is above threshold"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.redis.member_clusters[0]
  }

  alarm_actions = [
    aws_sns_topic.database_events.arn
  ]

  ok_actions = [
    aws_sns_topic.database_events.arn
  ]

  tags = var.common_tags
}

##############################################################
# Freeable Memory Alarm
##############################################################

resource "aws_cloudwatch_metric_alarm" "redis_memory" {

  alarm_name = "${var.project_name}-redis-low-memory"

  comparison_operator = "LessThanThreshold"

  evaluation_periods = 2

  metric_name = "FreeableMemory"

  namespace = "AWS/ElastiCache"

  period = 300

  statistic = "Average"

  threshold = 104857600

  alarm_description = "Redis freeable memory is low"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.redis.member_clusters[0]
  }

  alarm_actions = [
    aws_sns_topic.database_events.arn
  ]

  ok_actions = [
    aws_sns_topic.database_events.arn
  ]

  tags = var.common_tags
}

##############################################################
# Snapshot Count Alarm
##############################################################

resource "aws_cloudwatch_metric_alarm" "redis_snapshot_failures" {

  alarm_name = "${var.project_name}-redis-snapshot-failures"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 1

  metric_name = "SnapshotRetentionLimit"

  namespace = "AWS/ElastiCache"

  period = 3600

  statistic = "Average"

  threshold = 0

  alarm_description = "Redis snapshot retention issue detected"

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.replication_group_id
  }

  alarm_actions = [
    aws_sns_topic.database_events.arn
  ]

  tags = var.common_tags
}

##############################################################
# Lifecycle
##############################################################

resource "terraform_data" "redis_dependencies" {

  depends_on = [
    aws_elasticache_replication_group.redis,
    aws_cloudwatch_metric_alarm.redis_cpu,
    aws_cloudwatch_metric_alarm.redis_memory
  ]

  input = {
    replication_group = aws_elasticache_replication_group.redis.replication_group_id
  }
}