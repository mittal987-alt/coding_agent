##############################################################
# KMS Key for ECR Encryption
##############################################################

resource "aws_kms_key" "ecr" {

  description = "KMS Key for Amazon ECR"

  enable_key_rotation = true

  deletion_window_in_days = 30

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-ecr-kms"
    }
  )
}

resource "aws_kms_alias" "ecr" {

  name = "alias/${var.project_name}-ecr"

  target_key_id = aws_kms_key.ecr.key_id
}

##############################################################
# Backend Repository
##############################################################

resource "aws_ecr_repository" "backend" {

  name = "${var.project_name}/backend"

  image_tag_mutability = var.ecr_image_mutability

  image_scanning_configuration {

    scan_on_push = var.ecr_scan_on_push
  }

  encryption_configuration {

    encryption_type = "KMS"

    kms_key = aws_kms_key.ecr.arn
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-backend"
    }
  )
}

##############################################################
# Frontend Repository
##############################################################

resource "aws_ecr_repository" "frontend" {

  name = "${var.project_name}/frontend"

  image_tag_mutability = var.ecr_image_mutability

  image_scanning_configuration {

    scan_on_push = var.ecr_scan_on_push
  }

  encryption_configuration {

    encryption_type = "KMS"

    kms_key = aws_kms_key.ecr.arn
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-frontend"
    }
  )
}

##############################################################
# Backend Lifecycle Policy
##############################################################

resource "aws_ecr_lifecycle_policy" "backend" {

  repository = aws_ecr_repository.backend.name

  policy = jsonencode({

    rules = [

      {

        rulePriority = 1

        description = "Retain last 20 tagged images"

        selection = {

          tagStatus = "tagged"

          tagPrefixList = [
            "v"
          ]

          countType = "imageCountMoreThan"

          countNumber = 20
        }

        action = {

          type = "expire"
        }
      },

      {

        rulePriority = 2

        description = "Expire untagged images after 7 days"

        selection = {

          tagStatus = "untagged"

          countType = "sinceImagePushed"

          countUnit = "days"

          countNumber = 7
        }

        action = {

          type = "expire"
        }
      }
    ]
  })
}

##############################################################
# Frontend Lifecycle Policy
##############################################################

resource "aws_ecr_lifecycle_policy" "frontend" {

  repository = aws_ecr_repository.frontend.name

  policy = aws_ecr_lifecycle_policy.backend.policy
}

##############################################################
# Repository Policy
##############################################################

resource "aws_ecr_repository_policy" "backend" {

  repository = aws_ecr_repository.backend.name

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AllowEKS"

        Effect = "Allow"

        Principal = "*"

        Action = [

          "ecr:GetDownloadUrlForLayer",

          "ecr:BatchGetImage",

          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}

resource "aws_ecr_repository_policy" "frontend" {

  repository = aws_ecr_repository.frontend.name

  policy = aws_ecr_repository_policy.backend.policy
}