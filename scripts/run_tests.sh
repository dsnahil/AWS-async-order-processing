#!/bin/bash
# Complete test suite runner for both environments

set -e

echo "======================================"
echo "Complete Test Suite"
echo "======================================"
echo ""

# Function to run tests for an environment
run_test_suite() {
    local ENV=$1
    local API_ENDPOINT=$2
    
    echo ""
    echo "======================================"
    echo "Testing: $ENV"
    echo "======================================"
    echo ""
    
    # Collect metrics
    echo "Step 1: Collecting metrics..."
    if [ "$ENV" = "localstack" ]; then
        docker-compose -f docker-compose-localstack.yml run --rm \
            --entrypoint "python /scripts/collect_metrics.py localstack" \
            metrics-collector
    else
        # For AWS, run locally with proper credentials
        python3 scripts/collect_metrics.py aws
    fi
    echo ""
    
    # Run load test
    echo "Step 2: Running load test..."
    if [ "$ENV" = "localstack" ]; then
        docker-compose -f docker-compose-localstack.yml run --rm \
            --entrypoint "python /scripts/run_load_test.py localstack http://order-api:8081" \
            metrics-collector
    else
        python3 scripts/run_load_test.py aws "$API_ENDPOINT"
    fi
    echo ""
    
    echo -e "✓ Tests complete for $ENV"
}

# Check which environment to test
if [ "$1" = "localstack" ]; then
    echo "Testing LocalStack environment only..."
    run_test_suite "localstack" "http://localhost:8080"
    
elif [ "$1" = "aws" ]; then
    echo "Testing AWS environment only..."
    
    # Get ALB DNS from Terraform output
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    if [ -z "$ALB_DNS" ]; then
        echo "Error: Could not get ALB DNS. Is infrastructure deployed?"
        exit 1
    fi
    
    run_test_suite "aws" "http://$ALB_DNS"
    
elif [ "$1" = "both" ]; then
    echo "Testing both environments..."
    
    # Test LocalStack
    run_test_suite "localstack" "http://localhost:8080"
    
    # Test AWS
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    if [ -z "$ALB_DNS" ]; then
        echo "Warning: Could not get ALB DNS. Skipping AWS tests."
    else
        run_test_suite "aws" "http://$ALB_DNS"
    fi
    
    # Generate comparison report
    echo ""
    echo "======================================"
    echo "Generating Comparison Report"
    echo "======================================"
    echo ""
    docker-compose -f docker-compose-localstack.yml run --rm \
        --entrypoint "python /scripts/generate_report.py" \
        metrics-collector
    
else
    echo "Usage: $0 <environment>"
    echo "  environment: localstack | aws | both"
    exit 1
fi

echo ""
echo "======================================"
echo "✓ All tests complete!"
echo "======================================"
echo ""
echo "Results saved to: ./metrics/"
echo ""
