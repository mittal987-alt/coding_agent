##############################################################
# Project Information
##############################################################

variable "project_name" {

  description = "Project name"

  type = string

  default = "ai-platform"
}

variable "environment" {

  description = "Deployment environment"

  type = string

  default = "production"

  validation {

    condition = contains(
      ["development", "staging", "production"],
      var.environment
    )

    error_message = "Environment must be development, staging, or production."
  }
}

variable "owner" {

  description = "Project owner"

  type = string

  default = "DevOps Team"
}

##############################################################
# AWS Configuration
##############################################################

variable "aws_region" {

  description = "AWS Region"

  type = string

  default = "ap-south-1"
}

variable "availability_zones" {

  description = "Availability Zones"

  type = list(string)

  default = [
    "ap-south-1a",
    "ap-south-1b",
    "ap-south-1c"
  ]
}

##############################################################
# Networking
##############################################################

variable "vpc_cidr" {

  description = "VPC CIDR"

  type = string

  default = "10.0.0.0/16"
}

variable "public_subnets" {

  description = "Public subnet CIDRs"

  type = list(string)

  default = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]
}

variable "private_subnets" {

  description = "Private subnet CIDRs"

  type = list(string)

  default = [
    "10.0.11.0/24",
    "10.0.12.0/24",
    "10.0.13.0/24"
  ]
}

variable "database_subnets" {

  description = "Database subnet CIDRs"

  type = list(string)

  default = [
    "10.0.21.0/24",
    "10.0.22.0/24",
    "10.0.23.0/24"
  ]
}

##############################################################
# NAT Gateway
##############################################################

variable "enable_nat_gateway" {

  description = "Enable NAT Gateway"

  type = bool

  default = true
}

variable "single_nat_gateway" {

  description = "Use a single NAT Gateway"

  type = bool

  default = false
}

##############################################################
# DNS
##############################################################

variable "enable_dns_hostnames" {

  description = "Enable DNS hostnames"

  type = bool

  default = true
}

variable "enable_dns_support" {

  description = "Enable DNS support"

  type = bool

  default = true
}

##############################################################
# Tags
##############################################################

variable "common_tags" {

  description = "Common resource tags"

  type = map(string)

  default = {

    ManagedBy = "Terraform"

    Application = "AI Software Engineer"

    CostCenter = "Engineering"
  }
}
##############################################################
# EKS Cluster Configuration
##############################################################

variable "cluster_name" {

  description = "EKS Cluster Name"

  type = string

  default = "ai-platform"
}

variable "kubernetes_version" {

  description = "Kubernetes Version"

  type = string

  default = "1.31"
}

variable "cluster_endpoint_public_access" {

  description = "Enable public API endpoint"

  type = bool

  default = true
}

variable "cluster_endpoint_private_access" {

  description = "Enable private API endpoint"

  type = bool

  default = true
}

variable "cluster_public_access_cidrs" {

  description = "Allowed CIDRs for public API access"

  type = list(string)

  default = [
    "0.0.0.0/0"
  ]
}

##############################################################
# Cluster Logging
##############################################################

variable "cluster_enabled_log_types" {

  description = "Enabled control plane logs"

  type = list(string)

  default = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
}

##############################################################
# Secrets Encryption
##############################################################

variable "enable_cluster_encryption" {

  description = "Enable envelope encryption"

  type = bool

  default = true
}

##############################################################
# Managed Node Group
##############################################################

variable "node_group_name" {

  description = "Managed node group name"

  type = string

  default = "general"
}

variable "node_instance_types" {

  description = "EC2 instance types"

  type = list(string)

  default = [
    "t3.large"
  ]
}

variable "node_capacity_type" {

  description = "ON_DEMAND or SPOT"

  type = string

  default = "ON_DEMAND"

  validation {

    condition = contains(
      ["ON_DEMAND", "SPOT"],
      var.node_capacity_type
    )

    error_message = "Capacity type must be ON_DEMAND or SPOT."
  }
}

##############################################################
# Auto Scaling
##############################################################

variable "desired_size" {

  description = "Desired number of worker nodes"

  type = number

  default = 2
}

variable "min_size" {

  description = "Minimum worker nodes"

  type = number

  default = 2
}

variable "max_size" {

  description = "Maximum worker nodes"

  type = number

  default = 6
}

variable "max_unavailable" {

  description = "Maximum unavailable nodes during update"

  type = number

  default = 1
}

##############################################################
# Node Disk
##############################################################

variable "disk_size" {

  description = "Worker node disk size (GB)"

  type = number

  default = 50
}

##############################################################
# SSH Access
##############################################################

variable "enable_ssh_access" {

  description = "Enable SSH access to worker nodes"

  type = bool

  default = false
}

variable "ssh_key_name" {

  description = "EC2 Key Pair name"

  type = string

  default = ""
}

##############################################################
# EKS Add-ons
##############################################################

variable "eks_addons" {

  description = "EKS managed add-ons"

  type = map(string)

  default = {
    coredns            = "latest"
    kube-proxy         = "latest"
    vpc-cni            = "latest"
    eks-pod-identity-agent = "latest"
  }
}
##############################################################
# PostgreSQL (RDS)
##############################################################

variable "db_name" {

  description = "Database name"

  type = string

  default = "ai_platform"
}

variable "db_username" {

  description = "Database username"

  type = string

  default = "postgres"
}

variable "db_password" {

  description = "Database password"

  type = string

  sensitive = true
}

variable "db_instance_class" {

  description = "RDS instance type"

  type = string

  default = "db.t3.medium"
}

variable "db_allocated_storage" {

  description = "Allocated storage (GB)"

  type = number

  default = 100
}

variable "db_max_allocated_storage" {

  description = "Maximum autoscaling storage (GB)"

  type = number

  default = 500
}

variable "db_engine_version" {

  description = "PostgreSQL version"

  type = string

  default = "16.4"
}

variable "db_multi_az" {

  description = "Enable Multi-AZ deployment"

  type = bool

  default = true
}

variable "db_backup_retention_period" {

  description = "Backup retention period (days)"

  type = number

  default = 14
}

variable "db_backup_window" {

  description = "Preferred backup window"

  type = string

  default = "02:00-03:00"
}

variable "db_maintenance_window" {

  description = "Preferred maintenance window"

  type = string

  default = "Sun:03:00-Sun:04:00"
}

##############################################################
# ElastiCache (Redis)
##############################################################

variable "redis_node_type" {

  description = "Redis node type"

  type = string

  default = "cache.t3.medium"
}

variable "redis_engine_version" {

  description = "Redis engine version"

  type = string

  default = "7.1"
}

variable "redis_num_cache_clusters" {

  description = "Number of Redis cache nodes"

  type = number

  default = 2
}

##############################################################
# Amazon ECR
##############################################################

variable "ecr_image_mutability" {

  description = "ECR image tag mutability"

  type = string

  default = "IMMUTABLE"

  validation {

    condition = contains(
      ["MUTABLE", "IMMUTABLE"],
      var.ecr_image_mutability
    )

    error_message = "Must be MUTABLE or IMMUTABLE."
  }
}

variable "ecr_scan_on_push" {

  description = "Enable image scanning"

  type = bool

  default = true
}

##############################################################
# CloudWatch & Monitoring
##############################################################

variable "enable_container_insights" {

  description = "Enable CloudWatch Container Insights"

  type = bool

  default = true
}

variable "log_retention_days" {

  description = "CloudWatch log retention"

  type = number

  default = 30
}

##############################################################
# Security
##############################################################

variable "allowed_ingress_cidrs" {

  description = "Allowed ingress CIDRs"

  type = list(string)

  default = [
    "0.0.0.0/0"
  ]
}

##############################################################
# Feature Flags
##############################################################

variable "enable_deletion_protection" {

  description = "Enable deletion protection"

  type = bool

  default = true
}

variable "enable_monitoring" {

  description = "Enable monitoring resources"

  type = bool

  default = true
}