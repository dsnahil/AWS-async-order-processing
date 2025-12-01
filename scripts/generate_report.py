#!/usr/bin/env python3
"""
Comparison Report Generator
Analyzes metrics from both LocalStack and AWS deployments
Generates comparative analysis with visualizations
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

class ReportGenerator:
    def __init__(self, metrics_dir: str = "/metrics"):
        self.metrics_dir = metrics_dir
        self.localstack_data = None
        self.aws_data = None
    
    def load_latest_metrics(self):
        """Load the most recent metrics for each environment"""
        localstack_files = sorted(glob.glob(f"{self.metrics_dir}/localstack_*.json"))
        aws_files = sorted(glob.glob(f"{self.metrics_dir}/aws_*.json"))
        
        if localstack_files:
            with open(localstack_files[-1], 'r') as f:
                self.localstack_data = json.load(f)
            print(f"✓ Loaded LocalStack metrics: {localstack_files[-1]}")
        
        if aws_files:
            with open(aws_files[-1], 'r') as f:
                self.aws_data = json.load(f)
            print(f"✓ Loaded AWS metrics: {aws_files[-1]}")
        
        if not self.localstack_data or not self.aws_data:
            print("✗ Could not find metrics for both environments")
            return False
        return True
    
    def generate_cost_comparison_chart(self):
        """Generate cost comparison bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        environments = ['LocalStack', 'AWS']
        costs = [
            self.localstack_data['cost_metrics']['total_monthly_cost'],
            self.aws_data['cost_metrics']['total_monthly_cost']
        ]
        
        bars = ax.bar(environments, costs, color=['#3498db', '#e74c3c'])
        ax.set_ylabel('Monthly Cost (USD)', fontsize=12)
        ax.set_title('Monthly Infrastructure Cost Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(costs) * 1.2)
        
        # Add value labels on bars
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${cost:.2f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        output_file = f"{self.metrics_dir}/cost_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Generated cost comparison chart: {output_file}")
        plt.close()
    
    def generate_performance_comparison_chart(self):
        """Generate performance comparison chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Response time comparison
        environments = ['LocalStack', 'AWS']
        avg_times = [
            self.localstack_data['load_test_results']['average_response_time_ms'],
            self.aws_data['load_test_results']['average_response_time_ms']
        ]
        p95_times = [
            self.localstack_data['load_test_results']['p95_response_time_ms'],
            self.aws_data['load_test_results']['p95_response_time_ms']
        ]
        
        x = range(len(environments))
        width = 0.35
        
        bars1 = ax1.bar([i - width/2 for i in x], avg_times, width, label='Average', color='#3498db')
        bars2 = ax1.bar([i + width/2 for i in x], p95_times, width, label='P95', color='#e74c3c')
        
        ax1.set_ylabel('Response Time (ms)', fontsize=11)
        ax1.set_title('Response Time Comparison', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(environments)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Throughput comparison
        throughput = [
            self.localstack_data['load_test_results']['requests_per_second'],
            self.aws_data['load_test_results']['requests_per_second']
        ]
        
        bars = ax2.bar(environments, throughput, color=['#2ecc71', '#f39c12'])
        ax2.set_ylabel('Requests per Second', fontsize=11)
        ax2.set_title('Throughput Comparison', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars, throughput):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        output_file = f"{self.metrics_dir}/performance_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Generated performance comparison chart: {output_file}")
        plt.close()
    
    def generate_complexity_comparison(self):
        """Generate deployment complexity comparison"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        environments = ['LocalStack', 'AWS']
        setup_steps = [
            self.localstack_data['performance_metrics']['deployment_complexity']['setup_steps'],
            self.aws_data['performance_metrics']['deployment_complexity']['setup_steps']
        ]
        
        bars = ax.barh(environments, setup_steps, color=['#9b59b6', '#e67e22'])
        ax.set_xlabel('Number of Setup Steps', fontsize=11)
        ax.set_title('Deployment Complexity Comparison', fontsize=12, fontweight='bold')
        
        for bar, value in zip(bars, setup_steps):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{value} steps',
                   ha='left', va='center', fontsize=10, fontweight='bold', 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        output_file = f"{self.metrics_dir}/complexity_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Generated complexity comparison chart: {output_file}")
        plt.close()
    
    def generate_text_report(self):
        """Generate detailed text report"""
        report = []
        report.append("="*80)
        report.append("DEPLOYMENT COMPARISON REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*80)
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-"*80)
        report.append("")
        report.append("This report compares two deployment strategies for an asynchronous order")
        report.append("processing system:")
        report.append("  1. LocalStack - Local AWS emulation for development/testing")
        report.append("  2. AWS - Production cloud deployment with ECS Fargate")
        report.append("")
        
        # Cost Analysis
        report.append("COST ANALYSIS")
        report.append("-"*80)
        ls_cost = self.localstack_data['cost_metrics']
        aws_cost = self.aws_data['cost_metrics']
        
        report.append(f"LocalStack:")
        report.append(f"  Monthly Infrastructure Cost: ${ls_cost['total_monthly_cost']:.2f}")
        report.append(f"  Setup Time: {ls_cost['developer_time_cost']:.1f} hours")
        report.append(f"  Note: {ls_cost['notes']}")
        report.append("")
        
        report.append(f"AWS:")
        report.append(f"  Compute (ECS Fargate): ${aws_cost['compute_cost_monthly']:.2f}/month")
        report.append(f"  Networking (NAT, ALB): ${aws_cost['networking_cost_monthly']:.2f}/month")
        report.append(f"  Storage (Logs): ${aws_cost['storage_cost_monthly']:.2f}/month")
        report.append(f"  Total Monthly Cost: ${aws_cost['total_monthly_cost']:.2f}")
        report.append(f"  Setup Time: {aws_cost['developer_time_cost']:.1f} hours")
        report.append(f"  Note: {aws_cost['notes']}")
        report.append("")
        
        cost_diff = aws_cost['total_monthly_cost'] - ls_cost['total_monthly_cost']
        report.append(f"💰 Cost Difference: AWS costs ${cost_diff:.2f} more per month")
        report.append("")
        
        # Performance Analysis
        report.append("PERFORMANCE ANALYSIS")
        report.append("-"*80)
        ls_perf = self.localstack_data['load_test_results']
        aws_perf = self.aws_data['load_test_results']
        
        report.append(f"LocalStack:")
        report.append(f"  Throughput: {ls_perf['requests_per_second']} req/s")
        report.append(f"  Avg Response Time: {ls_perf['average_response_time_ms']}ms")
        report.append(f"  P95 Response Time: {ls_perf['p95_response_time_ms']}ms")
        report.append(f"  Error Rate: {ls_perf['error_rate_percent']}%")
        report.append(f"  Limitation: {ls_perf['throughput_limitation']}")
        report.append("")
        
        report.append(f"AWS:")
        report.append(f"  Throughput: {aws_perf['requests_per_second']} req/s")
        report.append(f"  Avg Response Time: {aws_perf['average_response_time_ms']}ms")
        report.append(f"  P95 Response Time: {aws_perf['p95_response_time_ms']}ms")
        report.append(f"  Error Rate: {aws_perf['error_rate_percent']}%")
        report.append(f"  Limitation: {aws_perf['throughput_limitation']}")
        report.append("")
        
        # Deployment Complexity
        report.append("DEPLOYMENT COMPLEXITY")
        report.append("-"*80)
        ls_complex = self.localstack_data['performance_metrics']['deployment_complexity']
        aws_complex = self.aws_data['performance_metrics']['deployment_complexity']
        
        report.append(f"LocalStack:")
        report.append(f"  Complexity Score: {ls_complex['complexity_score']}")
        report.append(f"  Setup Steps: {ls_complex['setup_steps']}")
        report.append(f"  Prerequisites: {', '.join(ls_complex['prerequisites'])}")
        report.append(f"  Network Setup: {ls_complex['network_setup']}")
        report.append("")
        
        report.append(f"AWS:")
        report.append(f"  Complexity Score: {aws_complex['complexity_score']}")
        report.append(f"  Setup Steps: {aws_complex['setup_steps']}")
        report.append(f"  Prerequisites: {', '.join(aws_complex['prerequisites'])}")
        report.append(f"  Network Setup: {aws_complex['network_setup']}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-"*80)
        report.append("")
        report.append("Use LocalStack when:")
        report.append("  ✓ Developing and testing locally without cloud costs")
        report.append("  ✓ Rapid iteration and debugging is needed")
        report.append("  ✓ Testing infrastructure as code (Terraform, CloudFormation)")
        report.append("  ✓ Learning AWS services without incurring charges")
        report.append("  ✓ CI/CD pipeline testing")
        report.append("")
        
        report.append("Use AWS when:")
        report.append("  ✓ Production deployment with real users")
        report.append("  ✓ Need for high availability and auto-scaling")
        report.append("  ✓ Global distribution and low-latency requirements")
        report.append("  ✓ Integration with other AWS managed services")
        report.append("  ✓ Compliance and security requirements")
        report.append("")
        
        report.append("="*80)
        
        # Save report
        output_file = f"{self.metrics_dir}/comparison_report.txt"
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"✓ Generated text report: {output_file}")
        
        # Also print to console
        print("\n" + '\n'.join(report))
    
    def generate_all_reports(self):
        """Generate all comparison reports"""
        print(f"\n{'='*60}")
        print("GENERATING COMPARISON REPORTS")
        print(f"{'='*60}\n")
        
        if not self.load_latest_metrics():
            return False
        
        try:
            self.generate_cost_comparison_chart()
            self.generate_performance_comparison_chart()
            self.generate_complexity_comparison()
            self.generate_text_report()
            
            print(f"\n{'='*60}")
            print("✓ All reports generated successfully!")
            print(f"Output directory: {self.metrics_dir}")
            print(f"{'='*60}\n")
            return True
        except Exception as e:
            print(f"\n✗ Error generating reports: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    generator = ReportGenerator()
    success = generator.generate_all_reports()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    import sys
    main()
