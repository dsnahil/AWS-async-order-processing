# --- 1. CONFIGURE AWS PROVIDER ---
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2" # <-- CHANGED
}

# --- 2. VPC & NETWORKING ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "assignment-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a" # <-- CHANGED
  map_public_ip_on_launch = true
  tags = {
    Name = "assignment-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2b" # <-- CHANGED
  map_public_ip_on_launch = true
  tags = {
    Name = "assignment-public-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "us-west-2a" # <-- CHANGED
  tags = {
    Name = "assignment-private-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "us-west-2b" # <-- CHANGED
  tags = {
    Name = "assignment-private-2"
  }
}

# --- 3. NETWORKING GATEWAYS & ROUTING ---
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "assignment-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    Name = "assignment-public-rt"
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id
  tags = {
    Name = "assignment-nat-gw"
  }
  depends_on = [aws_internet_gateway.gw]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = {
    Name = "assignment-private-rt"
  }
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}

# --- 4. SECURITY GROUPS ---
resource "aws_security_group" "alb" {
  name        = "assignment-alb-sg"
  description = "Allow HTTP traffic to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "assignment-ecs-tasks-sg"
  description = "Allow traffic from ALB to ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8081
    to_port         = 8081
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id] # Only allow from our ALB
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- 5. ALB (LOAD BALANCER) ---
resource "aws_lb" "main" {
  name               = "assignment-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "app" {
  name        = "assignment-tg-8081"
  port        = 8081 # Port our Go app listens on
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# --- 6. ECR (CONTAINER REGISTRY) ---
resource "aws_ecr_repository" "app" {
  name = "assignment-order-app"
}

# --- 7. ECS (CONTAINER SERVICE) ---
resource "aws_ecs_cluster" "main" {
  name = "assignment-cluster"
}

resource "aws_cloudwatch_log_group" "app" {
  name = "/ecs/assignment-app"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "assignment-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution.arn
  task_role_arn            = data.aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "order-api"
      image     = "public.ecr.aws/nginx/nginx:latest" # Placeholder
      essential = true
      portMappings = [
        {
          containerPort = 8081
          hostPort      = 8081
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = "us-west-2" # <-- CHANGED
          "awslogs-stream-prefix" = "api"
        }
      }
      environment = [
        { name = "SNS_TOPIC_ARN", value = aws_sns_topic.orders.arn }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "assignment-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution.arn
  task_role_arn            = data.aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "order-worker"
      image     = "public.ecr.aws/nginx/nginx:latest" # Placeholder
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = "us-west-2" # <-- CHANGED
          "awslogs-stream-prefix" = "worker"
        }
      }
      environment = [
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.orders.id },
        { name = "WORKER_GOROUTINES", value = "1" }
      ]
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "assignment-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "order-api"
    container_port   = 8081
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "worker" {
  name            = "assignment-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

# --- 8. IAM ROLES (Modified for AWS Learner Lab) ---

# We look up the LabRole and use it for BOTH execution and task.
data "aws_iam_role" "ecs_task_execution" {
  name = "LabRole"
}

data "aws_iam_role" "ecs_task" {
  name = "LabRole"
}

# --- 9. MESSAGING (SNS & SQS) ---
resource "aws_sns_topic" "orders" {
  name = "order-processing-events"
}

resource "aws_sqs_queue" "orders" {
  name                       = "order-processing-queue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600 # 4 days
  receive_wait_time_seconds  = 20
}

resource "aws_sns_topic_subscription" "orders_to_queue" {
  topic_arn = aws_sns_topic.orders.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.orders.arn
}

resource "aws_sqs_queue_policy" "orders_policy" {
  queue_url = aws_sqs_queue.orders.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.orders.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.orders.arn
          }
        }
      }
    ]
  })
}

# --- 10. OUTPUTS ---
output "alb_dns_name" {
  description = "The DNS name of the ALB"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}