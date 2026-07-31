##############################################################
# EKS Cluster IAM Role
##############################################################

resource "aws_iam_role" "eks_cluster" {

  name = "${var.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "eks.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]
  })

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-cluster-role"
    }
  )
}

##############################################################
# Cluster IAM Policy Attachments
##############################################################

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {

  role = aws_iam_role.eks_cluster.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_vpc_controller" {

  role = aws_iam_role.eks_cluster.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

##############################################################
# Node Group IAM Role
##############################################################

resource "aws_iam_role" "eks_nodes" {

  name = "${var.project_name}-eks-node-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "ec2.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]
  })

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-node-role"
    }
  )
}

##############################################################
# Node IAM Policy Attachments
##############################################################

resource "aws_iam_role_policy_attachment" "worker_nodes" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "cni_policy" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ssm_managed" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

##############################################################
# CloudWatch Log Group
##############################################################

resource "aws_cloudwatch_log_group" "eks" {

  name = "/aws/eks/${var.cluster_name}/cluster"

  retention_in_days = var.log_retention_days

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-logs"
    }
  )
}

##############################################################
# KMS Key for EKS Secret Encryption
##############################################################

resource "aws_kms_key" "eks" {

  description = "KMS key for EKS secrets encryption"

  enable_key_rotation = true

  deletion_window_in_days = 30

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eks-kms"
    }
  )
}

##############################################################
# KMS Alias
##############################################################

resource "aws_kms_alias" "eks" {

  name = "alias/${var.project_name}-eks"

  target_key_id = aws_kms_key.eks.key_id
}

##############################################################
# EKS Cluster
##############################################################

resource "aws_eks_cluster" "main" {

  name = var.cluster_name

  version = var.kubernetes_version

  role_arn = aws_iam_role.eks_cluster.arn

  enabled_cluster_log_types = var.cluster_enabled_log_types

  vpc_config {

    subnet_ids = concat(
      aws_subnet.private[*].id,
      aws_subnet.public[*].id
    )

    security_group_ids = [
      aws_security_group.eks_cluster.id
    ]

    endpoint_public_access = var.cluster_endpoint_public_access

    endpoint_private_access = var.cluster_endpoint_private_access

    public_access_cidrs = var.cluster_public_access_cidrs
  }

  encryption_config {

    provider {

      key_arn = aws_kms_key.eks.arn
    }

    resources = [
      "secrets"
    ]
  }

  depends_on = [

    aws_iam_role_policy_attachment.eks_cluster_policy,

    aws_iam_role_policy_attachment.eks_vpc_controller,

    aws_cloudwatch_log_group.eks
  ]

  tags = merge(
    var.common_tags,
    {
      Name = var.cluster_name
    }
  )
}

##############################################################
# OIDC Identity Provider
##############################################################

data "tls_certificate" "eks" {

  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    data.tls_certificate.eks.certificates[0].sha1_fingerprint
  ]

  url = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-oidc"
    }
  )
}

##############################################################
# EKS Managed Node Group
##############################################################

resource "aws_eks_node_group" "main" {

  cluster_name = aws_eks_cluster.main.name

  node_group_name = var.node_group_name

  node_role_arn = aws_iam_role.eks_nodes.arn

  subnet_ids = aws_subnet.private[*].id

  instance_types = var.node_instance_types

  capacity_type = var.node_capacity_type

  ami_type = "AL2023_x86_64_STANDARD"

  disk_size = var.disk_size

  scaling_config {

    desired_size = var.desired_size

    min_size = var.min_size

    max_size = var.max_size
  }

  update_config {

    max_unavailable = var.max_unavailable
  }

  labels = {

    role = "general"

    workload = "application"
  }

  dynamic "remote_access" {

    for_each = var.enable_ssh_access ? [1] : []

    content {

      ec2_ssh_key = var.ssh_key_name

      source_security_group_ids = [
        aws_security_group.eks_nodes.id
      ]
    }
  }

  depends_on = [

    aws_iam_role_policy_attachment.worker_nodes,

    aws_iam_role_policy_attachment.cni_policy,

    aws_iam_role_policy_attachment.ecr_readonly,

    aws_iam_role_policy_attachment.ssm_managed
  ]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.cluster_name}-node-group"
    }
  )
}

##############################################################
# EKS Managed Add-ons
##############################################################

resource "aws_eks_addon" "addons" {

  for_each = var.eks_addons

  cluster_name = aws_eks_cluster.main.name

  addon_name = each.key

  addon_version = each.value == "latest" ? null : each.value

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [
    aws_eks_node_group.main
  ]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${each.key}"
    }
  )
}

##############################################################
# Node Group Outputs (Local Values)
##############################################################

locals {

  cluster_endpoint = aws_eks_cluster.main.endpoint

  cluster_name = aws_eks_cluster.main.name

  cluster_certificate = aws_eks_cluster.main.certificate_authority[0].data

  oidc_provider_arn = aws_iam_openid_connect_provider.eks.arn
}
##############################################################
# EKS Managed Node Group
##############################################################

resource "aws_eks_node_group" "main" {

  cluster_name = aws_eks_cluster.main.name

  node_group_name = var.node_group_name

  node_role_arn = aws_iam_role.eks_nodes.arn

  subnet_ids = aws_subnet.private[*].id

  instance_types = var.node_instance_types

  capacity_type = var.node_capacity_type

  ami_type = "AL2023_x86_64_STANDARD"

  disk_size = var.disk_size

  scaling_config {

    desired_size = var.desired_size

    min_size = var.min_size

    max_size = var.max_size
  }

  update_config {

    max_unavailable = var.max_unavailable
  }

  labels = {

    role = "general"

    workload = "application"
  }

  dynamic "remote_access" {

    for_each = var.enable_ssh_access ? [1] : []

    content {

      ec2_ssh_key = var.ssh_key_name

      source_security_group_ids = [
        aws_security_group.eks_nodes.id
      ]
    }
  }

  depends_on = [

    aws_iam_role_policy_attachment.worker_nodes,

    aws_iam_role_policy_attachment.cni_policy,

    aws_iam_role_policy_attachment.ecr_readonly,

    aws_iam_role_policy_attachment.ssm_managed
  ]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.cluster_name}-node-group"
    }
  )
}

##############################################################
# EKS Managed Add-ons
##############################################################

resource "aws_eks_addon" "addons" {

  for_each = var.eks_addons

  cluster_name = aws_eks_cluster.main.name

  addon_name = each.key

  addon_version = each.value == "latest" ? null : each.value

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [
    aws_eks_node_group.main
  ]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${each.key}"
    }
  )
}

##############################################################
# Node Group Outputs (Local Values)
##############################################################

locals {

  cluster_endpoint = aws_eks_cluster.main.endpoint

  cluster_name = aws_eks_cluster.main.name

  cluster_certificate = aws_eks_cluster.main.certificate_authority[0].data

  oidc_provider_arn = aws_iam_openid_connect_provider.eks.arn
}