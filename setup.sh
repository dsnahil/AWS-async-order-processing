#!/bin/bash
# One-time setup script for the project

set -e

echo "======================================"
echo "Project Setup Script"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${RED}✗ Docker not found${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION installed${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi

# Optional checks
echo ""
echo "Optional tools (for AWS deployment):"

if command -v terraform &> /dev/null; then
    echo -e "${GREEN}✓ Terraform installed${NC}"
else
    echo -e "${YELLOW}⚠ Terraform not found (needed for AWS deployment)${NC}"
fi

if command -v aws &> /dev/null; then
    echo -e "${GREEN}✓ AWS CLI installed${NC}"
else
    echo -e "${YELLOW}⚠ AWS CLI not found (needed for AWS deployment)${NC}"
fi

# Create directories
echo ""
echo "Creating project directories..."
mkdir -p metrics/load_tests
mkdir -p localstack-data
mkdir -p diagrams
echo -e "${GREEN}✓ Directories created${NC}"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x scripts/*.sh
chmod +x init-aws.sh
echo -e "${GREEN}✓ Scripts are executable${NC}"

# Generate diagrams
echo ""
echo "Generating architecture diagrams..."
python3 scripts/generate_diagrams.py

# Test Docker
echo ""
echo "Testing Docker..."
if docker ps &> /dev/null; then
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
else
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi

# Pull required images
echo ""
echo "Pulling Docker images (this may take a few minutes)..."
docker pull localstack/localstack:latest
echo -e "${GREEN}✓ LocalStack image pulled${NC}"

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. For LocalStack deployment:"
echo "   ./scripts/deploy_localstack.sh"
echo ""
echo "2. For AWS deployment:"
echo "   ./scripts/deploy_aws.sh"
echo ""
echo "3. Run tests:"
echo "   ./scripts/run_tests.sh localstack"
echo ""
echo "4. View documentation:"
echo "   cat README.md"
echo "   cat DEPLOYMENT_ANALYSIS_REPORT.md"
echo ""
echo "For questions or issues, check:"
echo "  - README.md"
echo "  - INTERVIEW_PREP.md"
echo "  - GitHub: https://github.com/dsnahil/AWS-async-order-processing"
echo ""
