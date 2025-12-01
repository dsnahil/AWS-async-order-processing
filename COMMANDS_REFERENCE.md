# 🚀 COMMANDS CHEAT SHEET

Quick reference for all common commands you'll need.

---

## 🎬 Getting Started

### Initial Setup (One Time)
```bash
# Make scripts executable
chmod +x setup.sh scripts/*.sh init-aws.sh

# Run complete setup
./setup.sh
```

---

## 🐳 LocalStack Deployment

### Deploy LocalStack
```bash
# Automated deployment
./scripts/deploy_localstack.sh

# Manual deployment
docker-compose -f docker-compose-localstack.yml up -d
```

### Check Status
```bash
# Check all services
docker-compose -f docker-compose-localstack.yml ps

# Check LocalStack health
curl http://localhost:4566/_localstack/health

# Check API health
curl http://localhost:8082/health
```

### View Logs
```bash
# All services
docker-compose -f docker-compose-localstack.yml logs -f

# Specific service
docker-compose -f docker-compose-localstack.yml logs -f order-api
docker-compose -f docker-compose-localstack.yml logs -f order-worker-1
docker-compose -f docker-compose-localstack.yml logs -f localstack
```

### Stop/Restart
```bash
# Stop all services
docker-compose -f docker-compose-localstack.yml down

# Restart specific service
docker-compose -f docker-compose-localstack.yml restart order-api

# Rebuild and restart
docker-compose -f docker-compose-localstack.yml up -d --build
```

---

## ☁️ AWS Deployment

### Deploy to AWS
```bash
# Automated deployment
./scripts/deploy_aws.sh

# Manual steps
terraform init
terraform plan
terraform apply

# Get ALB DNS
terraform output alb_dns_name
```

### Update Services
```bash
# Force new deployment (after code changes)
aws ecs update-service \
  --cluster assignment-cluster \
  --service assignment-api-service \
  --force-new-deployment

aws ecs update-service \
  --cluster assignment-cluster \
  --service assignment-worker-service \
  --force-new-deployment
```

### Check Status
```bash
# List services
aws ecs list-services --cluster assignment-cluster

# Describe service
aws ecs describe-services \
  --cluster assignment-cluster \
  --services assignment-api-service assignment-worker-service

# View logs
aws logs tail /ecs/assignment-app --follow
```

### Destroy Infrastructure
```bash
terraform destroy
```

---

## 🧪 Testing

### Submit Test Orders
```bash
# LocalStack
curl -X POST http://localhost:8082/orders/async \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "items": [
      {"item_id": "item-a", "quantity": 2},
      {"item_id": "item-b", "quantity": 1}
    ]
  }'

# AWS (replace with your ALB DNS)
curl -X POST http://YOUR-ALB-DNS/orders/async \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "items": [
      {"item_id": "item-a", "quantity": 2}
    ]
  }'
```

### Run Load Tests
```bash
# Automated test suite
./scripts/run_tests.sh localstack
./scripts/run_tests.sh aws
./scripts/run_tests.sh both

# Manual Locust (with UI)
locust -f locustfile.py

# Headless Locust (LocalStack)
locust -f locustfile.py --headless \
  --users 10 --spawn-rate 2 --run-time 60s \
  --host http://localhost:8082

# Headless Locust (AWS)
locust -f locustfile.py --headless \
  --users 10 --spawn-rate 2 --run-time 60s \
  --host http://YOUR-ALB-DNS
```

---

## 📊 Metrics & Reports

### Collect Metrics
```bash
# LocalStack metrics
docker-compose -f docker-compose-localstack.yml run --rm \
  --entrypoint "python /scripts/collect_metrics.py localstack" \
  metrics-collector

# AWS metrics (run locally with AWS credentials)
python3 scripts/collect_metrics.py aws
```

### Generate Reports
```bash
# Generate comparison report
docker-compose -f docker-compose-localstack.yml run --rm \
  --entrypoint "python /scripts/generate_report.py" \
  metrics-collector

# View reports
cat metrics/comparison_report.txt
ls -lh metrics/*.png
```

### Generate Diagrams
```bash
python3 scripts/generate_diagrams.py

# View diagrams at:
# https://www.plantuml.com/plantuml/uml/
# Copy and paste .puml file contents
```

---

## 🐛 Debugging

### Check Docker
```bash
# Is Docker running?
docker ps

# Docker system info
docker info

# Free up space
docker system prune -a
```

### Check LocalStack
```bash
# LocalStack logs
docker logs localstack_main

# LocalStack health
curl http://localhost:4566/_localstack/health

# List SNS topics
aws --endpoint-url=http://localhost:4566 sns list-topics

# List SQS queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

# Get queue attributes
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes \
  --queue-url http://localhost:4566/000000000000/order-processing-queue \
  --attribute-names All
```

### Check API
```bash
# Test health endpoint
curl -v http://localhost:8082/health

# Check if port is in use
netstat -an | grep 8082
# or
lsof -i :8082

# Access API container
docker exec -it order-api-local /bin/sh
```

### Check Worker
```bash
# View worker logs
docker logs order-worker-1 -f

# Check SQS messages
aws --endpoint-url=http://localhost:4566 sqs receive-message \
  --queue-url http://localhost:4566/000000000000/order-processing-queue \
  --max-number-of-messages 1

# Access worker container
docker exec -it order-worker-1 /bin/sh
```

---

## 📦 Docker Management

### Build Images
```bash
# Build API
docker build -t order-api:latest ./order-api

# Build Worker
docker build -t order-worker:latest ./order-worker

# Build both
docker-compose -f docker-compose-localstack.yml build
```

### Clean Up
```bash
# Stop all containers
docker-compose -f docker-compose-localstack.yml down

# Remove volumes
docker-compose -f docker-compose-localstack.yml down -v

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# Full cleanup
docker system prune -a --volumes
```

---

## 📝 Documentation

### Convert Report to PDF
```bash
# Using Pandoc (recommended)
pandoc DEPLOYMENT_ANALYSIS_REPORT.md -o report.pdf

# Using VS Code
# Open .md file → Right-click → "Markdown PDF: Export (pdf)"

# Using wkhtmltopdf
markdown-pdf DEPLOYMENT_ANALYSIS_REPORT.md

# Online converter
# Visit: https://www.markdowntopdf.com/
```

### Generate Diagram Images
```bash
# 1. Install PlantUML (requires Java)
brew install plantuml  # macOS
apt-get install plantuml  # Ubuntu

# 2. Generate PNGs
cd diagrams
plantuml *.puml

# 3. View generated PNGs
ls -lh *.png
```

---

## 🔧 Python Environment

### Install Dependencies
```bash
# Install requirements
pip3 install -r requirements.txt

# Or with virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Python Scripts
```bash
# Collect metrics
python3 scripts/collect_metrics.py localstack

# Run load test
python3 scripts/run_load_test.py localstack http://localhost:8080

# Generate report
python3 scripts/generate_report.py

# Generate diagrams
python3 scripts/generate_diagrams.py
```

---

## 🎯 Git Commands

### Initial Commit
```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Complete Final Mastery assignment: LocalStack vs AWS deployment comparison"

# Add remote
git remote add origin https://github.com/dsnahil/AWS-async-order-processing.git

# Push
git push -u origin main
```

### Update Repository
```bash
# Stage changes
git add .

# Commit
git commit -m "Update documentation and scripts"

# Push
git push
```

---

## 🎤 Demo Commands (For Interview)

### Quick Demo Script
```bash
# 1. Show project structure
ls -la
cat README.md

# 2. Deploy LocalStack
./scripts/deploy_localstack.sh

# 3. Check health
curl http://localhost:8080/health

# 4. Submit order
curl -X POST http://localhost:8080/orders/async \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"items":[{"item_id":"demo","quantity":1}]}'

# 5. Show worker processing
docker-compose -f docker-compose-localstack.yml logs order-worker-1 --tail=20

# 6. Show metrics
cat metrics/comparison_report.txt

# 7. Show architecture
cat diagrams/system_architecture.puml
```

---

## 🆘 Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port 8080
lsof -ti:8080 | xargs kill -9

# Or change port in docker-compose-localstack.yml
# ports: - "8081:8081"
```

### Docker Daemon Not Running
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

### Cannot Connect to LocalStack
```bash
# Restart LocalStack
docker-compose -f docker-compose-localstack.yml restart localstack

# Wait for health check
sleep 10
curl http://localhost:4566/_localstack/health
```

### AWS Credentials Not Found
```bash
# Configure AWS
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

### Python Module Not Found
```bash
# Install requirements
pip3 install -r requirements.txt

# Or install specific module
pip3 install boto3 requests locust matplotlib
```

---

## 💡 Pro Tips

### Quick Status Check
```bash
# One-liner to check everything
docker ps && \
curl -s http://localhost:8080/health && \
curl -s http://localhost:4566/_localstack/health | jq
```

### Watch Logs in Real-Time
```bash
# Multiple terminals with split screen
docker-compose -f docker-compose-localstack.yml logs -f order-api &
docker-compose -f docker-compose-localstack.yml logs -f order-worker-1 &
```

### Continuous Testing
```bash
# Submit orders continuously
while true; do
  curl -X POST http://localhost:8080/orders/async \
    -H "Content-Type: application/json" \
    -d '{"customer_id":1,"items":[{"item_id":"test","quantity":1}]}'
  sleep 5
done
```

---

## 📚 Additional Resources

### Documentation Links
- LocalStack: https://docs.localstack.cloud/
- AWS ECS: https://docs.aws.amazon.com/ecs/
- Terraform: https://registry.terraform.io/providers/hashicorp/aws/
- Locust: https://docs.locust.io/

### Project Documentation
- Main README: `cat README.md`
- Analysis Report: `cat DEPLOYMENT_ANALYSIS_REPORT.md`
- Interview Prep: `cat INTERVIEW_PREP.md`
- Quick Reference: `cat QUICK_REFERENCE.md`

---

**💾 Save this file for quick reference during development and demos!**
