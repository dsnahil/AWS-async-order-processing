#!/bin/bash
# Deployment automation script for LocalStack environment

set -e  # Exit on error

echo "======================================"
echo "LocalStack Deployment Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo -e "${RED}✗ Docker is required but not installed.${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}✗ Docker Compose is required but not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p metrics/load_tests
mkdir -p localstack-data
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Build Docker images
echo "Building Docker images..."
docker-compose -f docker-compose-localstack.yml build
echo -e "${GREEN}✓ Images built${NC}"
echo ""

# Start LocalStack and services
echo "Starting LocalStack deployment..."
docker-compose -f docker-compose-localstack.yml up -d localstack order-api order-worker-1
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 15

# Check LocalStack health
echo "Checking LocalStack health..."
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://localhost:4566/_localstack/health | grep -q "running" || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    echo "  Waiting for LocalStack... (attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ LocalStack failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✓ LocalStack is healthy${NC}"

# Check API health
echo "Checking Order API health..."
RETRY_COUNT=0
until curl -s http://localhost:8080/health | grep -q "200" || [ $RETRY_COUNT -eq 10 ]; do
    echo "  Waiting for API... (attempt $((RETRY_COUNT+1))/10)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq 10 ]; then
    echo -e "${YELLOW}⚠ API may not be ready, but continuing...${NC}"
else
    echo -e "${GREEN}✓ Order API is healthy${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✓ LocalStack Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "Services running:"
echo "  • LocalStack:  http://localhost:4566"
echo "  • Order API:   http://localhost:8080"
echo "  • Order Worker: Running in background"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose-localstack.yml logs -f"
echo ""
echo "To stop:"
echo "  docker-compose -f docker-compose-localstack.yml down"
echo ""
