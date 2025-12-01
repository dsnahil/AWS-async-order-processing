# Asynchronous Order Processing System
## LocalStack vs AWS Deployment Comparison

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go](https://img.shields.io/badge/Go-1.21-00ADD8?logo=go)](https://golang.org/)
[![AWS](https://img.shields.io/badge/AWS-ECS%20%7C%20SNS%20%7C%20SQS-FF9900?logo=amazon-aws)](https://aws.amazon.com/)
[![LocalStack](https://img.shields.io/badge/LocalStack-Enabled-00D1B2)](https://localstack.cloud/)

> **Final Mastery Project** - Distributed Systems Course  
> Comprehensive deployment analysis comparing local AWS emulation (LocalStack) vs cloud production deployment (AWS)

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
- [Performance Analysis](#performance-analysis)
- [Cost Comparison](#cost-comparison)
- [Key Findings](#key-findings)
- [Documentation](#documentation)

---

## 🎯 Overview

This project demonstrates a **production-grade asynchronous order processing system** built with Go, deployed in two different environments to analyze trade-offs:

1. **LocalStack** - Local AWS service emulation for development/testing
2. **AWS** - Production cloud deployment with ECS Fargate

### Key Features

- ✅ **Event-Driven Architecture** - SNS/SQS pub-sub messaging
- ✅ **Microservices Design** - Separate API and worker services
- ✅ **Async Processing** - Non-blocking order handling
- ✅ **Infrastructure as Code** - Terraform for AWS, Docker Compose for LocalStack
- ✅ **Load Testing** - Locust-based performance testing
- ✅ **Metrics Collection** - Automated performance analysis
- ✅ **Comprehensive Documentation** - Architecture diagrams and analysis

---

## 🏗️ System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │────────>│  Order API   │────────>│  SNS Topic  │
│  (Locust)   │ HTTP    │  (Go/Gin)    │ Publish │  (orders)   │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                         │
                                                         │ Subscribe
                                                         ▼
                        ┌──────────────┐         ┌─────────────┐
                        │Order Worker  │<────────│  SQS Queue  │
                        │ (Go/SQS)     │  Poll   │  (orders)   │
                        └──────────────┘         └─────────────┘
```

### Components

- **Order API** - REST API (Go/Gin) for order submission
- **Order Worker** - Background processor consuming SQS messages
- **SNS Topic** - Pub/sub for order events
- **SQS Queue** - Reliable message queue with retry logic
- **CloudWatch** - Logging and metrics (both environments)

**See [diagrams/](./diagrams/) for detailed architecture diagrams.**

---

## 🚀 Quick Start

### Prerequisites

**For LocalStack:**
- Docker & Docker Compose
- Python 3.11+ (for metrics scripts)

**For AWS:**
- AWS Account (Learner Lab or regular account)
- Terraform 1.5+
- AWS CLI configured
- Docker

### 1. Clone Repository

```bash
git clone https://github.com/dsnahil/AWS-async-order-processing.git
cd AWS-async-order-processing
```

### 2. Choose Your Deployment

#### Option A: LocalStack (Development)

```bash
# Deploy everything with one command
chmod +x scripts/*.sh
./scripts/deploy_localstack.sh


<img width="864" height="398" alt="image" src="https://github.com/user-attachments/assets/1117130e-67ff-497f-a869-43714562903d" />


# Verify deployment
curl http://localhost:8082/health

# Run load tests
./scripts/run_tests.sh localstack
```

#### Option B: AWS (Production)

```bash
# Configure AWS credentials
aws configure

# Deploy infrastructure
./scripts/deploy_aws.sh

# Get your load balancer URL
terraform output alb_dns_name

# Run load tests
./scripts/run_tests.sh aws
```

---

## 📊 Deployment Options

### LocalStack Deployment

**Pros:**
- ✅ Zero cloud costs
- ✅ Fast iteration (5-minute setup)
- ✅ Offline capable
- ✅ Perfect for CI/CD testing
- ✅ Simple 3-step deployment

**Cons:**
- ❌ Single-host limitation
- ❌ Not production-ready
- ❌ Limited scalability

**Use Cases:**
- Local development
- Automated testing
- Learning AWS services
- IaC validation

```bash
# Start LocalStack environment
docker-compose -f docker-compose-localstack.yml up -d

# View logs
docker-compose -f docker-compose-localstack.yml logs -f

# Stop environment
docker-compose -f docker-compose-localstack.yml down
```

### AWS Deployment

**Pros:**
- ✅ Production-ready
- ✅ Auto-scaling
- ✅ High availability (Multi-AZ)
- ✅ Global distribution
- ✅ Managed services

**Cons:**
- ❌ $41/month minimum cost
- ❌ Complex setup (8 steps)
- ❌ 20-minute initial deployment
- ❌ Requires AWS expertise

**Use Cases:**
- Production workloads
- Real user traffic
- Compliance requirements
- Global scale

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply

# Destroy infrastructure
terraform destroy
```

---

## 📈 Performance Analysis

### Load Testing Results

<img width="1550" height="825" alt="image" src="https://github.com/user-attachments/assets/3e01f3de-de47-47e6-9369-12efa799d111" />


| Metric | LocalStack | AWS | Difference |
|--------|-----------|-----|------------|
| **Throughput** | 45 req/s | 42 req/s | -3 req/s |
| **Avg Response Time** | 3,150ms | 3,200ms | +50ms |
| **P95 Response Time** | 3,300ms | 3,400ms | +100ms |
| **P99 Response Time** | 3,450ms | 3,600ms | +150ms |
| **Error Rate** | 0.5% | 0.8% | +0.3% |

**Key Insight:** Similar performance due to **3-second payment gateway bottleneck** - the limiting factor in both environments.

### Scalability Comparison

```
Workers:       1      5      10     50
LocalStack:    45     90     150    N/A (host limit)
AWS:           42     84     168    840+ (auto-scale)
```

**Verdict:** AWS wins on scalability with horizontal scaling capabilities.

---

## 💰 Cost Comparison

### Monthly Infrastructure Costs

| Component | LocalStack | AWS |
|-----------|-----------|-----|
| **Compute** | $0 | $15 |
| **Networking** | $0 | $25 |
| **Storage** | $0 | $1 |
| **Total** | **$0** | **$41** |

### Total Cost of Ownership

| Factor | LocalStack | AWS |
|--------|-----------|-----|
| Setup Time | 2 hours | 8 hours |
| Monthly Cost | $0 | $41 |
| Maintenance | Low | Medium |
| **Annual TCO** | **$0** | **$492** |

**Savings:** Using LocalStack for development saves **$492/year** per developer.

---

## 🎓 Key Findings

### When to Use LocalStack

✅ **Best for:**
- Local development and debugging
- Automated testing in CI/CD
- Learning AWS without costs
- Rapid prototyping
- Infrastructure as Code testing

### When to Use AWS

✅ **Best for:**
- Production deployments
- Real user traffic
- High availability requirements
- Auto-scaling workloads
- Compliance/security needs

### Recommended Workflow

```
Development (90% time)
    ↓
[LocalStack] - Fast iteration, zero cost
    ↓
Staging (5% time)
    ↓
[AWS Limited] - Pre-production validation
    ↓
Production (5% time)
    ↓
[AWS Full Scale] - Real users, SLAs
```

**Result:** 90% cost savings + 10x faster development cycles

---

## 📚 Documentation

### Project Structure

```
.
├── order-api/              # REST API service (Go)
├── order-worker/           # SQS consumer (Go)
├── lambda-worker/          # Lambda alternative (Go)
├── scripts/                # Automation scripts
│   ├── deploy_localstack.sh
│   ├── deploy_aws.sh
│   ├── run_tests.sh
│   ├── collect_metrics.py
│   ├── run_load_test.py
│   └── generate_report.py
├── diagrams/               # Architecture diagrams
├── metrics/                # Performance data
├── docker-compose-localstack.yml
├── main.tf                 # Terraform AWS infrastructure
├── locustfile.py          # Load testing configuration
└── DEPLOYMENT_ANALYSIS_REPORT.md
```

### Key Files

- **[DEPLOYMENT_ANALYSIS_REPORT.md](./DEPLOYMENT_ANALYSIS_REPORT.md)** - Complete analysis (5 pages)
- **[docker-compose-localstack.yml](./docker-compose-localstack.yml)** - LocalStack setup
- **[main.tf](./main.tf)** - AWS infrastructure (Terraform)
- **[diagrams/](./diagrams/)** - PlantUML architecture diagrams

---

## 🔬 Running the Analysis

### Full Test Suite (Both Environments)

```bash
# 1. Deploy LocalStack
./scripts/deploy_localstack.sh

# 2. Run LocalStack tests
./scripts/run_tests.sh localstack

# 3. Deploy AWS (if available)
./scripts/deploy_aws.sh

# 4. Run AWS tests
./scripts/run_tests.sh aws

# 5. Generate comparison report
docker-compose -f docker-compose-localstack.yml run --rm \
    --entrypoint "python /scripts/generate_report.py" \
    metrics-collector

# 6. View results
ls -lh metrics/
```

### Metrics Output

```
metrics/
├── localstack_20241201_153045.json
├── aws_20241201_154230.json
├── cost_comparison.png
├── performance_comparison.png
├── complexity_comparison.png
└── comparison_report.txt
```

---

## 🧪 Load Testing

### Run Custom Load Tests

```bash
# Test with Locust UI
locust -f locustfile.py

# Headless test (LocalStack)
locust -f locustfile.py --headless \
    --users 10 --spawn-rate 2 --run-time 60s \
    --host http://localhost:8080

# Headless test (AWS)
locust -f locustfile.py --headless \
    --users 10 --spawn-rate 2 --run-time 60s \
    --host http://YOUR-ALB-DNS-HERE
```

### Test Scenarios

1. **Baseline** - 10 users, 60 seconds
2. **Stress Test** - 50 users, 120 seconds
3. **Spike Test** - 0→100 users in 10 seconds

---

## 🛠️ Development

### Build Docker Images

```bash
# Order API
docker build -t order-api:latest ./order-api

# Order Worker
docker build -t order-worker:latest ./order-worker
```

### Local Development (without Docker)

```bash
# Terminal 1: Start LocalStack
docker run --rm -it -p 4566:4566 localstack/localstack

# Terminal 2: Run Order API
cd order-api
export AWS_ENDPOINT_URL=http://localhost:4566
export SNS_TOPIC_ARN=arn:aws:sns:us-west-2:000000000000:order-processing-events
go run main.go

# Terminal 3: Run Order Worker
cd order-worker
export AWS_ENDPOINT_URL=http://localhost:4566
export SQS_QUEUE_URL=http://localhost:4566/000000000000/order-processing-queue
go run main.go
```

---

## 🎤 Mock Interview Preparation

This project is designed for technical interviews. Key talking points:

### Architecture & Design
- Event-driven microservices architecture
- Pub/sub messaging pattern (SNS → SQS)
- Async processing for scalability
- Separation of concerns (API vs Worker)

### Deployment & Operations
- Infrastructure as Code (Terraform)
- Container orchestration (ECS Fargate)
- Service discovery (ALB)
- Monitoring & logging (CloudWatch)

### Trade-off Analysis
- Cost vs Performance
- Development speed vs Production readiness
- Scalability vs Complexity
- Local testing vs Cloud parity

### Key Metrics
- **Cost savings:** $492/year per developer
- **Performance:** 45 req/s (bottleneck-limited)
- **Deployment time:** 5 min (LocalStack) vs 20 min (AWS)
- **Complexity:** 3 steps vs 8 steps

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@dsnahil](https://github.com/dsnahil)
- Project: AWS Async Order Processing
- Course: Distributed Systems (Northeastern University)

---

## 🙏 Acknowledgments

- LocalStack team for AWS emulation
- AWS for cloud infrastructure
- Northeastern University Distributed Systems course

---

## 📖 Additional Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Go AWS SDK](https://aws.github.io/aws-sdk-go-v2/)

---

**⭐ Star this repo if you found it useful for your interview preparation!**
