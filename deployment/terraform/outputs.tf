##############################################################
# VPC Outputs
##############################################################

output "vpc_id" {

  description = "VPC ID"

  value = aws_vpc.main.id
}

output "public_subnet_ids" {

  description = "Public subnet IDs"

  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {

  description = "Private subnet IDs"

  value = aws_subnet.private[*].id
}

output "database_subnet_ids" {

  description = "Database subnet IDs"

  value = aws_subnet.database[*].id
}

##############################################################
# EKS Outputs
##############################################################

output "cluster_name" {

  description = "EKS Cluster Name"

  value = aws_eks_cluster.main.name
}

output "cluster_endpoint" {

  description = "EKS API Endpoint"

  value = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority" {

  description = "Cluster CA"

  value = aws_eks_cluster.main.certificate_authority[0].data

  sensitive = true
}

output "cluster_oidc_provider_arn" {

  description = "OIDC Provider ARN"

  value = aws_iam_openid_connect_provider.eks.arn
}

##############################################################
# Database Outputs
##############################################################

output "postgres_endpoint" {

  description = "PostgreSQL Endpoint"

  value = aws_db_instance.postgres.endpoint
}

output "postgres_port" {

  description = "PostgreSQL Port"

  value = aws_db_instance.postgres.port
}

##############################################################
# Redis Outputs
##############################################################

output "redis_primary_endpoint" {

  description = "Redis Primary Endpoint"

  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_reader_endpoint" {

  description = "Redis Reader Endpoint"

  value = aws_elasticache_replication_group.redis.reader_endpoint_address
}

##############################################################
# ECR Outputs
##############################################################

output "backend_repository_url" {

  description = "Backend ECR Repository"

  value = aws_ecr_repository.backend.repository_url
}

output "frontend_repository_url" {

  description = "Frontend ECR Repository"

  value = aws_ecr_repository.frontend.repository_url
}

##############################################################
# IAM Outputs
##############################################################

output "eks_cluster_role_arn" {

  description = "EKS Cluster Role ARN"

  value = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_arn" {

  description = "EKS Node Role ARN"

  value = aws_iam_role.eks_nodes.arn
}

##############################################################
# kubectl Helper
##############################################################

output "configure_kubectl_command" {

  description = "Command to configure kubectl"

  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}

##############################################################
# Useful Console URLs
##############################################################

output "aws_region" {

  description = "AWS Region"

  value = var.aws_region
}

output "account_id" {

  description = "AWS Account ID"

  value = data.aws_caller_identity.current.account_id
}