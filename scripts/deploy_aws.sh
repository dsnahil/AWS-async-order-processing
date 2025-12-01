#!/bin/bash
# Deployment automation script for AWS environment

set -e  # Exit on error

echo "======================================"
echo "AWS Deployment Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}✗ Terraform is required but not installed.${NC}" >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo -e "${RED}✗ AWS CLI is required but not installed.${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}✗ Docker is required but not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo "Please configure AWS credentials first:"
    echo "  aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo ""

# Initialize Terraform
echo "Initializing Terraform..."
terraform init
echo -e "${GREEN}✓ Terraform initialized${NC}"
echo ""

# Plan infrastructure
echo "Planning infrastructure deployment..."
terraform plan -out=tfplan
echo ""
read -p "Do you want to apply this plan? (yes/no): " APPLY_CONFIRM

if [ "$APPLY_CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Apply infrastructure
echo ""
echo "Deploying infrastructure to AWS..."
terraform apply tfplan
echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# Get outputs
ECR_REPO=$(terraform output -raw ecr_repository_url)
ALB_DNS=$(terraform output -raw alb_dns_name)

echo "======================================"
echo "Infrastructure Details"
echo "======================================"
echo "ECR Repository: $ECR_REPO"
echo "Load Balancer:  http://$ALB_DNS"
echo ""

# Build and push Docker images
echo "Building and pushing Docker images..."
echo ""

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $ECR_REPO
echo -e "${GREEN}✓ Logged in to ECR${NC}"

# Build and push Order API
echo "Building Order API image..."
docker build -t order-api:latest ./order-api
docker tag order-api:latest $ECR_REPO:order-api-latest
docker push $ECR_REPO:order-api-latest
echo -e "${GREEN}✓ Order API image pushed${NC}"

# Build and push Order Worker
echo "Building Order Worker image..."
docker build -t order-worker:latest ./order-worker
docker tag order-worker:latest $ECR_REPO:order-worker-latest
docker push $ECR_REPO:order-worker-latest
echo -e "${GREEN}✓ Order Worker image pushed${NC}"

echo ""
echo "======================================"
echo "Updating ECS Task Definitions"
echo "======================================"

# Update task definitions with actual image URIs
# This would require additional AWS CLI commands to update the task definitions
echo -e "${YELLOW}⚠ Manual step required:${NC}"
echo "Update the ECS task definitions with the new image URIs:"
echo "  Order API:    $ECR_REPO:order-api-latest"
echo "  Order Worker: $ECR_REPO:order-worker-latest"
echo ""
echo "Then force new deployment:"
echo "  aws ecs update-service --cluster assignment-cluster --service assignment-api-service --force-new-deployment"
echo "  aws ecs update-service --cluster assignment-cluster --service assignment-worker-service --force-new-deployment"
echo ""

echo "======================================"
echo -e "${GREEN}✓ AWS Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "Services:"
echo "  • API Endpoint: http://$ALB_DNS"
echo "  • Region:       us-west-2"
echo ""
echo "To check service status:"
echo "  aws ecs describe-services --cluster assignment-cluster --services assignment-api-service assignment-worker-service"
echo ""
echo "To view logs:"
echo "  aws logs tail /ecs/assignment-app --follow"
echo ""
echo "To destroy infrastructure:"
echo "  terraform destroy"
echo ""
