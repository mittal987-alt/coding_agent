##############################################################
# VPC Endpoints Security Group
##############################################################

resource "aws_security_group" "vpc_endpoints" {

  name        = "${var.project_name}-vpc-endpoints"
  description = "Security group for VPC Interface Endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {

    description = "HTTPS from VPC"

    from_port = 443

    to_port = 443

    protocol = "tcp"

    cidr_blocks = [
      var.vpc_cidr
    ]
  }

  egress {

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc-endpoints"
    }
  )
}

##############################################################
# EKS Cluster Security Group
##############################################################

resource "aws_security_group" "eks_cluster" {

  name        = "${var.project_name}-eks-cluster"

  description = "Security Group for EKS Control Plane"

  vpc_id = aws_vpc.main.id

  ingress {

    description = "Kubernetes API"

    from_port = 443

    to_port = 443

    protocol = "tcp"

    cidr_blocks = var.allowed_ingress_cidrs
  }

  egress {

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-cluster-sg"
    }
  )
}

##############################################################
# Worker Nodes Security Group
##############################################################

resource "aws_security_group" "eks_nodes" {

  name = "${var.project_name}-eks-workers"

  description = "Security Group for EKS Worker Nodes"

  vpc_id = aws_vpc.main.id

  ingress {

    description = "Worker to Worker"

    from_port = 0

    to_port = 65535

    protocol = "tcp"

    self = true
  }

  ingress {

    description = "Control Plane"

    from_port = 1025

    to_port = 65535

    protocol = "tcp"

    security_groups = [
      aws_security_group.eks_cluster.id
    ]
  }

  ingress {

    description = "HTTPS"

    from_port = 443

    to_port = 443

    protocol = "tcp"

    security_groups = [
      aws_security_group.eks_cluster.id
    ]
  }

  egress {

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-workers-sg"
    }
  )
}

##############################################################
# PostgreSQL Security Group
##############################################################

resource "aws_security_group" "postgres" {

  name = "${var.project_name}-postgres"

  description = "PostgreSQL Security Group"

  vpc_id = aws_vpc.main.id

  ingress {

    description = "PostgreSQL"

    from_port = 5432

    to_port = 5432

    protocol = "tcp"

    security_groups = [
      aws_security_group.eks_nodes.id
    ]
  }

  egress {

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-postgres-sg"
    }
  )
}

##############################################################
# Redis Security Group
##############################################################

resource "aws_security_group" "redis" {

  name        = "${var.project_name}-redis"
  description = "Security Group for ElastiCache Redis"
  vpc_id      = aws_vpc.main.id

  ingress {

    description = "Redis from EKS Worker Nodes"

    from_port = 6379
    to_port   = 6379
    protocol  = "tcp"

    security_groups = [
      aws_security_group.eks_nodes.id
    ]
  }

  egress {

    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-sg"
    }
  )
}

##############################################################
# Allow Nodes -> Cluster API
##############################################################

resource "aws_security_group_rule" "nodes_to_cluster_https" {

  type = "ingress"

  from_port = 443
  to_port   = 443

  protocol = "tcp"

  security_group_id = aws_security_group.eks_cluster.id

  source_security_group_id = aws_security_group.eks_nodes.id

  description = "Worker nodes communicate with control plane"
}

##############################################################
# Allow Cluster -> Nodes
##############################################################

resource "aws_security_group_rule" "cluster_to_nodes" {

  type = "egress"

  from_port = 1025
  to_port   = 65535

  protocol = "tcp"

  security_group_id = aws_security_group.eks_cluster.id

  source_security_group_id = aws_security_group.eks_nodes.id

  description = "Control plane communicates with worker nodes"
}

##############################################################
# Worker Nodes Self Communication
##############################################################

resource "aws_security_group_rule" "node_self" {

  type = "ingress"

  from_port = 0
  to_port   = 65535

  protocol = "-1"

  security_group_id = aws_security_group.eks_nodes.id

  self = true

  description = "Allow inter-node communication"
}

##############################################################
# HTTPS Access to VPC Endpoints
##############################################################

resource "aws_security_group_rule" "eks_to_endpoints" {

  type = "ingress"

  from_port = 443
  to_port   = 443

  protocol = "tcp"

  security_group_id = aws_security_group.vpc_endpoints.id

  source_security_group_id = aws_security_group.eks_nodes.id

  description = "Worker nodes access Interface Endpoints"
}

##############################################################
# PostgreSQL Security Hardening
##############################################################

resource "aws_security_group_rule" "postgres_from_nodes" {

  type = "ingress"

  from_port = 5432
  to_port   = 5432

  protocol = "tcp"

  security_group_id = aws_security_group.postgres.id

  source_security_group_id = aws_security_group.eks_nodes.id

  description = "Allow PostgreSQL access only from worker nodes"
}

##############################################################
# Redis Security Hardening
##############################################################

resource "aws_security_group_rule" "redis_from_nodes" {

  type = "ingress"

  from_port = 6379
  to_port   = 6379

  protocol = "tcp"

  security_group_id = aws_security_group.redis.id

  source_security_group_id = aws_security_group.eks_nodes.id

  description = "Allow Redis access only from worker nodes"
}