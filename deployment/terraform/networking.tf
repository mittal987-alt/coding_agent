##############################################################
# VPC
##############################################################

resource "aws_vpc" "main" {

  cidr_block = var.vpc_cidr

  enable_dns_support   = var.enable_dns_support
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

##############################################################
# Internet Gateway
##############################################################

resource "aws_internet_gateway" "main" {

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-igw"
    }
  )
}

##############################################################
# Public Subnets
##############################################################

resource "aws_subnet" "public" {

  count = length(var.public_subnets)

  vpc_id = aws_vpc.main.id

  cidr_block = var.public_subnets[count.index]

  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-${count.index + 1}"

      Tier = "Public"

      "kubernetes.io/role/elb" = "1"
    }
  )
}

##############################################################
# Private Subnets
##############################################################

resource "aws_subnet" "private" {

  count = length(var.private_subnets)

  vpc_id = aws_vpc.main.id

  cidr_block = var.private_subnets[count.index]

  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = false

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-${count.index + 1}"

      Tier = "Private"

      "kubernetes.io/role/internal-elb" = "1"
    }
  )
}

##############################################################
# Database Subnets
##############################################################

resource "aws_subnet" "database" {

  count = length(var.database_subnets)

  vpc_id = aws_vpc.main.id

  cidr_block = var.database_subnets[count.index]

  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = false

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-database-${count.index + 1}"

      Tier = "Database"
    }
  )
}

##############################################################
# Elastic IPs for NAT Gateways
##############################################################

resource "aws_eip" "nat" {

  count = var.enable_nat_gateway ? (
    var.single_nat_gateway ? 1 : length(var.public_subnets)
  ) : 0

  domain = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-nat-eip-${count.index + 1}"
    }
  )

  depends_on = [
    aws_internet_gateway.main
  ]
}
##############################################################
# NAT Gateways
##############################################################

resource "aws_nat_gateway" "main" {

  count = var.enable_nat_gateway ? (
    var.single_nat_gateway ? 1 : length(var.public_subnets)
  ) : 0

  allocation_id = aws_eip.nat[count.index].id

  subnet_id = aws_subnet.public[
    var.single_nat_gateway ? 0 : count.index
  ].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-nat-${count.index + 1}"
    }
  )

  depends_on = [
    aws_internet_gateway.main
  ]
}

##############################################################
# Public Route Table
##############################################################

resource "aws_route_table" "public" {

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-rt"
    }
  )
}

##############################################################
# Public Internet Route
##############################################################

resource "aws_route" "public_internet_access" {

  route_table_id = aws_route_table.public.id

  destination_cidr_block = "0.0.0.0/0"

  gateway_id = aws_internet_gateway.main.id
}

##############################################################
# Private Route Tables
##############################################################

resource "aws_route_table" "private" {

  count = length(var.private_subnets)

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-rt-${count.index + 1}"
    }
  )
}

##############################################################
# Private Internet Routes via NAT
##############################################################

resource "aws_route" "private_nat_gateway" {

  count = var.enable_nat_gateway ? length(var.private_subnets) : 0

  route_table_id = aws_route_table.private[count.index].id

  destination_cidr_block = "0.0.0.0/0"

  nat_gateway_id = aws_nat_gateway.main[
    var.single_nat_gateway ? 0 : count.index
  ].id
}

##############################################################
# Public Route Table Associations
##############################################################

resource "aws_route_table_association" "public" {

  count = length(var.public_subnets)

  subnet_id = aws_subnet.public[count.index].id

  route_table_id = aws_route_table.public.id
}

##############################################################
# Private Route Table Associations
##############################################################

resource "aws_route_table_association" "private" {

  count = length(var.private_subnets)

  subnet_id = aws_subnet.private[count.index].id

  route_table_id = aws_route_table.private[count.index].id
}
##############################################################
# Database Route Tables
##############################################################

resource "aws_route_table" "database" {

  count = length(var.database_subnets)

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-database-rt-${count.index + 1}"
    }
  )
}

##############################################################
# Database Route Table Associations
##############################################################

resource "aws_route_table_association" "database" {

  count = length(var.database_subnets)

  subnet_id = aws_subnet.database[count.index].id

  route_table_id = aws_route_table.database[count.index].id
}

##############################################################
# Database Subnet Group
##############################################################

resource "aws_db_subnet_group" "main" {

  name = "${var.project_name}-db-subnet-group"

  subnet_ids = aws_subnet.database[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-db-subnet-group"
    }
  )
}

##############################################################
# S3 Gateway VPC Endpoint
##############################################################

resource "aws_vpc_endpoint" "s3" {

  vpc_id = aws_vpc.main.id

  service_name = "com.amazonaws.${var.aws_region}.s3"

  vpc_endpoint_type = "Gateway"

  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id
  )

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-s3-endpoint"
    }
  )
}

##############################################################
# ECR API Endpoint
##############################################################

resource "aws_vpc_endpoint" "ecr_api" {

  vpc_id = aws_vpc.main.id

  service_name = "com.amazonaws.${var.aws_region}.ecr.api"

  vpc_endpoint_type = "Interface"

  subnet_ids = aws_subnet.private[*].id

  security_group_ids = [
    aws_security_group.vpc_endpoints.id
  ]

  private_dns_enabled = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-ecr-api"
    }
  )
}

##############################################################
# ECR Docker Endpoint
##############################################################

resource "aws_vpc_endpoint" "ecr_dkr" {

  vpc_id = aws_vpc.main.id

  service_name = "com.amazonaws.${var.aws_region}.ecr.dkr"

  vpc_endpoint_type = "Interface"

  subnet_ids = aws_subnet.private[*].id

  security_group_ids = [
    aws_security_group.vpc_endpoints.id
  ]

  private_dns_enabled = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-ecr-dkr"
    }
  )
}

##############################################################
# CloudWatch Logs Endpoint
##############################################################

resource "aws_vpc_endpoint" "logs" {

  vpc_id = aws_vpc.main.id

  service_name = "com.amazonaws.${var.aws_region}.logs"

  vpc_endpoint_type = "Interface"

  subnet_ids = aws_subnet.private[*].id

  security_group_ids = [
    aws_security_group.vpc_endpoints.id
  ]

  private_dns_enabled = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-logs-endpoint"
    }
  )
}