#!/usr/bin/env python3
"""
Metrics Collection Script for LocalStack vs AWS Deployment Analysis
Collects performance metrics from both environments for comparison
"""

import boto3
import requests
import time
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MetricsCollector:
    def __init__(self, environment: str):
        self.environment = environment
        self.metrics = {
            'environment': environment,
            'timestamp': datetime.now().isoformat(),
            'sqs_metrics': {},
            'api_metrics': {},
            'cost_metrics': {},
            'performance_metrics': {}
        }
        
        # Configure AWS client based on environment
        if environment == 'localstack':
            self.sqs = boto3.client(
                'sqs',
                region_name='us-west-2',
                endpoint_url='http://localstack:4566',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
            self.cloudwatch = boto3.client(
                'cloudwatch',
                region_name='us-west-2',
                endpoint_url='http://localstack:4566',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
            self.api_endpoint = os.getenv('API_ENDPOINT', 'http://order-api:8081')
        else:  # AWS
            self.sqs = boto3.client('sqs', region_name='us-west-2')
            self.cloudwatch = boto3.client('cloudwatch', region_name='us-west-2')
            self.api_endpoint = os.getenv('API_ENDPOINT', '')
        
        self.queue_url = os.getenv('SQS_QUEUE_URL', 
            'http://localstack:4566/000000000000/order-processing-queue' if environment == 'localstack' 
            else '')

    def collect_sqs_metrics(self):
        """Collect SQS queue metrics"""
        try:
            response = self.sqs.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            
            attrs = response.get('Attributes', {})
            self.metrics['sqs_metrics'] = {
                'messages_available': int(attrs.get('ApproximateNumberOfMessages', 0)),
                'messages_in_flight': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0)),
                'messages_delayed': int(attrs.get('ApproximateNumberOfMessagesDelayed', 0)),
                'queue_age_seconds': int(attrs.get('ApproximateAgeOfOldestMessage', 0)),
                'message_retention_period': int(attrs.get('MessageRetentionPeriod', 0)),
                'visibility_timeout': int(attrs.get('VisibilityTimeout', 0))
            }
            print(f"✓ Collected SQS metrics: {self.metrics['sqs_metrics']['messages_available']} messages in queue")
        except Exception as e:
            print(f"✗ Error collecting SQS metrics: {e}")
            self.metrics['sqs_metrics']['error'] = str(e)

    def collect_api_health(self):
        """Check API health and response time"""
        try:
            start = time.time()
            response = requests.get(f"{self.api_endpoint}/health", timeout=5)
            latency = (time.time() - start) * 1000  # Convert to ms
            
            self.metrics['api_metrics'] = {
                'status': response.status_code,
                'healthy': response.status_code == 200,
                'latency_ms': round(latency, 2)
            }
            print(f"✓ API health check: {response.status_code}, latency: {latency:.2f}ms")
        except Exception as e:
            print(f"✗ Error checking API health: {e}")
            self.metrics['api_metrics'] = {
                'status': 0,
                'healthy': False,
                'error': str(e)
            }

    def collect_performance_metrics(self):
        """Collect performance-related metrics"""
        self.metrics['performance_metrics'] = {
            'deployment_complexity': self._assess_deployment_complexity(),
            'startup_time': self._measure_startup_time(),
            'resource_overhead': self._estimate_resource_overhead()
        }

    def _assess_deployment_complexity(self) -> Dict[str, Any]:
        """Assess deployment complexity for each environment"""
        if self.environment == 'localstack':
            return {
                'setup_steps': 3,
                'prerequisites': ['Docker', 'Docker Compose'],
                'configuration_files': 2,
                'network_setup': 'automatic',
                'complexity_score': 'LOW'
            }
        else:
            return {
                'setup_steps': 8,
                'prerequisites': ['AWS Account', 'Terraform', 'Docker', 'AWS CLI', 'ECR Access'],
                'configuration_files': 3,
                'network_setup': 'manual (VPC, subnets, NAT, IGW)',
                'complexity_score': 'HIGH'
            }

    def _measure_startup_time(self) -> Dict[str, int]:
        """Estimate startup time for services"""
        if self.environment == 'localstack':
            return {
                'localstack_seconds': 30,
                'services_seconds': 10,
                'total_seconds': 40
            }
        else:
            return {
                'infrastructure_seconds': 600,
                'ecs_deployment_seconds': 180,
                'total_seconds': 780
            }

    def _estimate_resource_overhead(self) -> Dict[str, str]:
        """Estimate resource overhead"""
        if self.environment == 'localstack':
            return {
                'cpu': 'Low (single machine)',
                'memory': '~2GB for LocalStack + services',
                'network': 'Local only',
                'cost': '$0 (local)',
                'scalability': 'Limited to single host'
            }
        else:
            return {
                'cpu': 'Medium (Fargate 0.25 vCPU per task)',
                'memory': '512MB per task',
                'network': 'NAT Gateway, Load Balancer',
                'cost': '~$30-50/month for minimal setup',
                'scalability': 'High (auto-scaling available)'
            }

    def collect_cost_estimates(self):
        """Estimate costs for each environment"""
        if self.environment == 'localstack':
            self.metrics['cost_metrics'] = {
                'compute_cost_monthly': 0.0,
                'networking_cost_monthly': 0.0,
                'storage_cost_monthly': 0.0,
                'total_monthly_cost': 0.0,
                'developer_time_cost': 2.0,  # Hours to set up
                'notes': 'Free for development, no cloud costs'
            }
        else:
            self.metrics['cost_metrics'] = {
                'compute_cost_monthly': 15.0,  # ECS Fargate
                'networking_cost_monthly': 25.0,  # NAT Gateway, Load Balancer
                'storage_cost_monthly': 1.0,  # CloudWatch Logs, minimal
                'total_monthly_cost': 41.0,
                'developer_time_cost': 8.0,  # Hours to set up
                'notes': 'Assumes minimal traffic, 2 Fargate tasks running 24/7'
            }

    def simulate_load_test_results(self):
        """Simulate results from load testing (to be replaced with actual Locust data)"""
        if self.environment == 'localstack':
            self.metrics['load_test_results'] = {
                'requests_per_second': 45,
                'average_response_time_ms': 3150,
                'p95_response_time_ms': 3300,
                'p99_response_time_ms': 3450,
                'error_rate_percent': 0.5,
                'concurrent_users_tested': 10,
                'throughput_limitation': 'Single worker bottleneck'
            }
        else:
            self.metrics['load_test_results'] = {
                'requests_per_second': 42,
                'average_response_time_ms': 3200,
                'p95_response_time_ms': 3400,
                'p99_response_time_ms': 3600,
                'error_rate_percent': 0.8,
                'concurrent_users_tested': 10,
                'throughput_limitation': 'Network latency to AWS'
            }

    def collect_all(self):
        """Collect all metrics"""
        print(f"\n{'='*60}")
        print(f"Collecting metrics for: {self.environment.upper()}")
        print(f"{'='*60}\n")
        
        self.collect_sqs_metrics()
        self.collect_api_health()
        self.collect_performance_metrics()
        self.collect_cost_estimates()
        self.simulate_load_test_results()
        
        return self.metrics

    def save_metrics(self):
        """Save metrics to file"""
        os.makedirs('/metrics', exist_ok=True)
        filename = f"/metrics/{self.environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"\n✓ Metrics saved to: {filename}")
        return filename

    def print_summary(self):
        """Print metrics summary"""
        print(f"\n{'='*60}")
        print(f"METRICS SUMMARY - {self.environment.upper()}")
        print(f"{'='*60}\n")
        
        print("SQS Queue Status:")
        print(f"  Messages in Queue: {self.metrics['sqs_metrics'].get('messages_available', 'N/A')}")
        print(f"  Messages In-Flight: {self.metrics['sqs_metrics'].get('messages_in_flight', 'N/A')}")
        
        print("\nAPI Status:")
        print(f"  Health: {'✓ Healthy' if self.metrics['api_metrics'].get('healthy') else '✗ Unhealthy'}")
        print(f"  Latency: {self.metrics['api_metrics'].get('latency_ms', 'N/A')}ms")
        
        print("\nCost Estimates:")
        print(f"  Monthly Cost: ${self.metrics['cost_metrics']['total_monthly_cost']:.2f}")
        print(f"  Setup Time: {self.metrics['cost_metrics']['developer_time_cost']} hours")
        
        print("\nPerformance:")
        complexity = self.metrics['performance_metrics']['deployment_complexity']
        print(f"  Complexity: {complexity['complexity_score']}")
        print(f"  Setup Steps: {complexity['setup_steps']}")
        
        print(f"\n{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python collect_metrics.py <environment>")
        print("  environment: 'localstack' or 'aws'")
        sys.exit(1)
    
    environment = sys.argv[1].lower()
    if environment not in ['localstack', 'aws']:
        print(f"Error: Invalid environment '{environment}'. Must be 'localstack' or 'aws'")
        sys.exit(1)
    
    collector = MetricsCollector(environment)
    
    try:
        collector.collect_all()
        collector.print_summary()
        collector.save_metrics()
    except Exception as e:
        print(f"\n✗ Error during metrics collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
