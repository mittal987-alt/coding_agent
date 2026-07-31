# AI Software Engineer Platform

Production-grade AWS infrastructure built using Terraform.

---

# Architecture

```
                        Internet
                            │
                     Application Load Balancer
                            │
                      Amazon EKS Cluster
                 ┌────────────┴────────────┐
                 │                         │
          Backend Pods              Frontend Pods
                 │
     ┌───────────┼────────────┐
     │           │            │
 Amazon RDS   Redis      Qdrant
 PostgreSQL ElastiCache  Vector DB
```

---

# Components

Infrastructure includes:

- Amazon VPC
- Public Subnets
- Private Subnets
- Database Subnets
- Internet Gateway
- NAT Gateway
- Amazon EKS
- Amazon RDS PostgreSQL
- Amazon ElastiCache Redis
- Amazon ECR
- CloudWatch
- IAM Roles
- KMS Encryption
- VPC Endpoints

---

# Prerequisites

Install:

- Terraform >= 1.8
- AWS CLI v2
- kubectl
- Helm
- Docker

Verify versions

```bash
terraform version
aws --version
kubectl version --client
helm version
docker version
```

---

# AWS Authentication

```bash
aws configure
```

Verify

```bash
aws sts get-caller-identity
```

---

# Clone Repository

```bash
git clone <repository>

cd deployment/terraform
```

---

# Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Update

```
db_password

aws_region

project_name

environment
```

---

# Initialize Terraform

```bash
terraform init
```

---

# Validate

```bash
terraform validate
```

---

# Format

```bash
terraform fmt -recursive
```

---

# Preview Changes

```bash
terraform plan
```

---

# Deploy

```bash
terraform apply
```

or

```bash
terraform apply -auto-approve
```

---

# Configure kubectl

```bash
aws eks update-kubeconfig \
--region ap-south-1 \
--name ai-platform
```

---

# Verify Cluster

```bash
kubectl get nodes

kubectl get pods -A

kubectl get ns
```

---

# Outputs

```bash
terraform output

terraform output cluster_endpoint

terraform output backend_repository_url
```

---

# Remote State (Recommended)

Use:

- Amazon S3
- DynamoDB Lock Table

Example backend configuration:

```hcl
terraform {

  backend "s3" {

    bucket = "terraform-state"

    key = "ai-platform/terraform.tfstate"

    region = "ap-south-1"

    dynamodb_table = "terraform-lock"

    encrypt = true
  }

}
```

---

# Destroy

```bash
terraform destroy
```

---

# Estimated AWS Resources

- 1 VPC
- 3 Public Subnets
- 3 Private Subnets
- 3 Database Subnets
- 1 Internet Gateway
- NAT Gateways
- Amazon EKS Cluster
- Managed Node Group
- Amazon RDS PostgreSQL
- Amazon ElastiCache Redis
- Amazon ECR Repositories
- IAM Roles
- CloudWatch
- KMS Keys

---

# Best Practices

- Use remote state
- Enable encryption
- Rotate secrets regularly
- Keep Terraform providers updated
- Use immutable container images
- Review `terraform plan` before applying
- Enable CloudWatch monitoring
- Restrict network access with security groups
- Protect production resources from accidental deletion

---

# Troubleshooting

Initialize providers again:

```bash
terraform init -upgrade
```

Refresh state:

```bash
terraform refresh
```

Validate configuration:

```bash
terraform validate
```

Inspect resources:

```bash
terraform state list
```

---

# Project Structure

```
deployment/
└── terraform/
    ├── versions.tf
    ├── providers.tf
    ├── variables.tf
    ├── networking.tf
    ├── security.tf
    ├── eks.tf
    ├── rds.tf
    ├── elasticache.tf
    ├── ecr.tf
    ├── outputs.tf
    ├── terraform.tfvars.example
    └── README.md
```

---

# Deployment Flow

```
Terraform Init
        │
Terraform Plan
        │
Terraform Apply
        │
Create AWS Infrastructure
        │
Configure kubectl
        │
Deploy Helm Chart
        │
Verify Services
        │
Production Ready
```