#!/usr/bin/env python3
"""
Load Testing Script using Locust programmatically
Runs load tests and generates detailed performance reports
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime

class LoadTester:
    def __init__(self, environment: str, host: str):
        self.environment = environment
        self.host = host
        self.results_dir = "/metrics/load_tests"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_load_test(self, users: int = 10, spawn_rate: int = 2, duration: str = "60s"):
        """Run a Locust load test"""
        print(f"\n{'='*60}")
        print(f"Running load test on {self.environment.upper()}")
        print(f"Target: {self.host}")
        print(f"Users: {users}, Spawn Rate: {spawn_rate}, Duration: {duration}")
        print(f"{'='*60}\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_prefix = f"{self.results_dir}/{self.environment}_{timestamp}"
        
        cmd = [
            "locust",
            "-f", "/scripts/locustfile.py",
            "--headless",
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", duration,
            "--host", self.host,
            "--csv", csv_prefix,
            "--html", f"{csv_prefix}_report.html"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"Error running load test: {result.stderr}")
                return None
            
            # Parse results
            stats_file = f"{csv_prefix}_stats.csv"
            if os.path.exists(stats_file):
                print(f"✓ Load test complete. Results saved to {csv_prefix}_*")
                return self._parse_results(stats_file)
            else:
                print("✗ Could not find results file")
                return None
                
        except Exception as e:
            print(f"✗ Error during load test: {e}")
            return None
    
    def _parse_results(self, stats_file: str):
        """Parse Locust CSV results"""
        # This is a simplified parser - in practice you'd read the CSV
        return {
            'test_completed': True,
            'results_file': stats_file
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_load_test.py <environment> <host>")
        print("  environment: 'localstack' or 'aws'")
        print("  host: API endpoint URL (e.g., http://order-api:8081)")
        sys.exit(1)
    
    environment = sys.argv[1].lower()
    host = sys.argv[2]
    
    tester = LoadTester(environment, host)
    results = tester.run_load_test(users=10, spawn_rate=2, duration="60s")
    
    if results:
        print("\n✓ Load test completed successfully")
    else:
        print("\n✗ Load test failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
