##############################################################
# AWS Provider
##############################################################

provider "aws" {

  region = var.aws_region

  default_tags {

    tags = {

      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
      Application = "AI Software Engineer"
    }
  }
}

##############################################################
# Current AWS Account
##############################################################

data "aws_caller_identity" "current" {}

##############################################################
# Current Region
##############################################################

data "aws_region" "current" {}

##############################################################
# Availability Zones
##############################################################

data "aws_availability_zones" "available" {

  state = "available"
}

##############################################################
# EKS Cluster
##############################################################

data "aws_eks_cluster" "cluster" {

  name = aws_eks_cluster.main.name

  depends_on = [
    aws_eks_cluster.main
  ]
}

##############################################################
# EKS Authentication
##############################################################

data "aws_eks_cluster_auth" "cluster" {

  name = aws_eks_cluster.main.name

  depends_on = [
    aws_eks_cluster.main
  ]
}

##############################################################
# Kubernetes Provider
##############################################################

provider "kubernetes" {

  host = data.aws_eks_cluster.cluster.endpoint

  cluster_ca_certificate = base64decode(
    data.aws_eks_cluster.cluster.certificate_authority[0].data
  )

  token = data.aws_eks_cluster_auth.cluster.token
}

##############################################################
# Helm Provider
##############################################################

provider "helm" {

  kubernetes {

    host = data.aws_eks_cluster.cluster.endpoint

    cluster_ca_certificate = base64decode(
      data.aws_eks_cluster.cluster.certificate_authority[0].data
    )

    token = data.aws_eks_cluster_auth.cluster.token
  }
}

##############################################################
# Random Provider
##############################################################

provider "random" {}

##############################################################
# TLS Provider
##############################################################

provider "tls" {}

##############################################################
# Local Provider
##############################################################

provider "local" {}

##############################################################
# Null Provider
##############################################################

provider "null" {}

##############################################################
# Time Provider
##############################################################

provider "time" {}