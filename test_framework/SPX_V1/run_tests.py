#!/usr/bin/env python3
"""
SPX_V1 Testing Framework - Command Line Test Runner

This script executes the comprehensive test suite for the SPX_V1 strategy
and generates detailed test result reports with timestamps.

Usage:
    python run_tests.py [options]
    
Options:
    --category <category>    Run tests for specific category
    --markers <markers>      Run tests with specific markers (unit, integration, ui, etc.)
    --verbose               Enable verbose output
    --coverage              Generate coverage report
    --report-only           Generate report from last test run
    --help                  Show this help message

Examples:
    python run_tests.py                           # Run all tests
    python run_tests.py --category data           # Run data management tests only
    python run_tests.py --markers "unit and not slow"  # Run unit tests, exclude slow tests
    python run_tests.py --verbose --coverage      # Run with verbose output and coverage
"""

import sys
import os
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import json
import time
import signal


class TestRunner:
    """Command line test runner for SPX_V1 testing framework."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.result_file = self.results_dir / f"test_result_{self.timestamp}.txt"
        self.json_file = self.results_dir / f"test_result_{self.timestamp}.json"
        self.start_time = None
        self.end_time = None
        self.test_results = {
            "framework": "SPX_V1",
            "timestamp": self.timestamp,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "test_details": [],
            "summary": {},
            "coverage": {}
        }
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n\n🛑 Test execution interrupted by signal {signum}")
            self.save_partial_results()
            sys.exit(1)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def print_header(self):
        """Print test execution header."""
        header = f"""
{'='*80}
🧪 SPX_V1 TESTING FRAMEWORK
{'='*80}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Test Directory: {self.test_dir}
Results File: {self.result_file}
{'='*80}
"""
        print(header)
        self.write_to_file(header)
    
    def write_to_file(self, content):
        """Write content to result file."""
        with open(self.result_file, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
    
    def run_category_tests(self, category):
        """Run tests for a specific category."""
        category_map = {
            'data': 'tests/test_data_management.py',
            'parameters': 'tests/test_strategy_parameters.py',
            'trading': 'tests/test_trading_logic.py',
            'risk': 'tests/test_risk_management.py',
            'costs': 'tests/test_transaction_costs.py',
            'analytics': 'tests/test_performance_analytics.py',
            'edge_cases': 'tests/test_edge_cases.py',
            'integration': 'tests/test_integration.py',
            'performance': 'tests/test_performance.py',
            'compliance': 'tests/test_regulatory_compliance.py',
            'ui': 'tests/test_ui_components.py'
        }
        
        if category not in category_map:
            available = ', '.join(category_map.keys())
            raise ValueError(f"Unknown category '{category}'. Available categories: {available}")
        
        return category_map[category]
    
    def build_pytest_command(self, args):
        """Build pytest command with specified options."""
        cmd = [sys.executable, '-m', 'pytest']
        
        # Base options
        cmd.extend(['-v', '--tb=short', '--strict-markers'])
        
        # Test path
        if args.category:
            test_path = self.run_category_tests(args.category)
            cmd.append(test_path)
        else:
            cmd.append('tests/')
        
        # Markers
        if args.markers:
            cmd.extend(['-m', args.markers])
        
        # Verbose output
        if args.verbose:
            cmd.extend(['-s', '--tb=long'])
        
        # Coverage
        if args.coverage:
            cmd.extend([
                '--cov=.',
                '--cov-report=html:htmlcov',
                '--cov-report=term-missing',
                '--cov-report=json:coverage.json'
            ])
        
        # Output format
        cmd.extend(['--junit-xml=pytest_results.xml'])
        
        return cmd
    
    def parse_pytest_output(self, output):
        """Parse pytest output to extract test results."""
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Test execution tracking
            if '::test_' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                parts = line.split('::')
                if len(parts) >= 2:
                    test_file = parts[0].replace('tests/', '').replace('.py', '')
                    test_name = parts[1].split()[0]
                    status = 'PASSED' if 'PASSED' in line else 'FAILED' if 'FAILED' in line else 'SKIPPED'
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Log test execution
                    execution_msg = f"[{timestamp}] Executing test: {test_name}"
                    print(execution_msg)
                    self.write_to_file(execution_msg)
                    
                    # Log test result
                    result_msg = f"[{timestamp}] {test_name}: {status}"
                    if 'FAILED' in line:
                        result_msg += " ❌"
                    elif 'PASSED' in line:
                        result_msg += " ✅"
                    elif 'SKIPPED' in line:
                        result_msg += " ⏭️"
                    
                    print(result_msg)
                    self.write_to_file(result_msg)
                    
                    # Store test details
                    self.test_results["test_details"].append({
                        "file": test_file,
                        "name": test_name,
                        "status": status,
                        "timestamp": timestamp
                    })
                    
                    # Update counters
                    if status == 'PASSED':
                        self.test_results["passed"] += 1
                    elif status == 'FAILED':
                        self.test_results["failed"] += 1
                    elif status == 'SKIPPED':
                        self.test_results["skipped"] += 1
                    
                    self.test_results["total_tests"] += 1
    
    def run_tests(self, args):
        """Execute the test suite."""
        self.setup_signal_handlers()
        self.print_header()
        
        # Record start time
        self.start_time = datetime.now()
        self.test_results["start_time"] = self.start_time.isoformat()
        
        start_msg = f"🚀 Starting test execution at {self.start_time.strftime('%H:%M:%S')}\n"
        print(start_msg)
        self.write_to_file(start_msg)
        
        try:
            # Build pytest command
            cmd = self.build_pytest_command(args)
            cmd_str = ' '.join(cmd)
            
            command_msg = f"Command: {cmd_str}\n"
            print(command_msg)
            self.write_to_file(command_msg)
            
            # Change to test directory
            os.chdir(self.test_dir)
            
            # Execute pytest
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            output_lines = []
            
            # Read output in real-time
            for line in iter(process.stdout.readline, ''):
                output_lines.append(line.rstrip())
                
                # Parse and display test results immediately
                if '::test_' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                    self.parse_pytest_output(line)
                elif line.strip() and not line.startswith('='):
                    # Display other pytest output (filtered)
                    print(line.rstrip())
                    self.write_to_file(line.rstrip())
            
            # Wait for process to complete
            process.wait()
            return_code = process.returncode
            
        except Exception as e:
            error_msg = f"❌ Error executing tests: {str(e)}"
            print(error_msg)
            self.write_to_file(error_msg)
            return_code = 1
        
        # Record end time
        self.end_time = datetime.now()
        self.test_results["end_time"] = self.end_time.isoformat()
        duration = self.end_time - self.start_time
        self.test_results["duration"] = str(duration)
        
        # Generate summary
        self.generate_summary(return_code)
        
        return return_code
    
    def generate_summary(self, return_code):
        """Generate test execution summary."""
        summary_lines = [
            "\n" + "="*80,
            "📊 TEST EXECUTION SUMMARY",
            "="*80,
            f"Framework: SPX_V1",
            f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {self.test_results['duration']}",
            "",
            f"Total Tests: {self.test_results['total_tests']}",
            f"✅ Passed: {self.test_results['passed']}",
            f"❌ Failed: {self.test_results['failed']}",
            f"⏭️  Skipped: {self.test_results['skipped']}",
            "",
        ]
        
        # Calculate success rate
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100
            summary_lines.append(f"Success Rate: {success_rate:.1f}%")
        
        # Overall result
        if return_code == 0 and self.test_results['failed'] == 0:
            summary_lines.append("🎉 OVERALL RESULT: ALL TESTS PASSED")
        else:
            summary_lines.append("💥 OVERALL RESULT: SOME TESTS FAILED")
        
        summary_lines.extend([
            "",
            f"📁 Detailed results saved to: {self.result_file}",
            f"📄 JSON results saved to: {self.json_file}",
            "="*80
        ])
        
        summary = '\n'.join(summary_lines)
        print(summary)
        self.write_to_file(summary)
        
        # Update test results summary
        self.test_results["summary"] = {
            "overall_result": "PASS" if return_code == 0 and self.test_results['failed'] == 0 else "FAIL",
            "success_rate": (self.test_results['passed'] / self.test_results['total_tests'] * 100) if self.test_results['total_tests'] > 0 else 0
        }
        
        # Save JSON results
        self.save_json_results()
    
    def save_json_results(self):
        """Save test results to JSON file."""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Warning: Could not save JSON results: {e}")
    
    def save_partial_results(self):
        """Save partial results when interrupted."""
        self.end_time = datetime.now()
        self.test_results["end_time"] = self.end_time.isoformat()
        if self.start_time:
            duration = self.end_time - self.start_time
            self.test_results["duration"] = str(duration)
        
        partial_msg = "\n⚠️  Test execution was interrupted. Partial results saved."
        print(partial_msg)
        self.write_to_file(partial_msg)
        
        self.save_json_results()
    
    def generate_report_only(self):
        """Generate report from existing test results."""
        # Find most recent results file
        json_files = list(self.results_dir.glob("test_result_*.json"))
        
        if not json_files:
            print("❌ No previous test results found.")
            return 1
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            print(f"📄 Generating report from: {latest_file}")
            
            # Display summary
            print("\n" + "="*80)
            print("📊 TEST RESULTS REPORT")
            print("="*80)
            print(f"Framework: {results.get('framework', 'SPX_V1')}")
            print(f"Timestamp: {results.get('timestamp', 'Unknown')}")
            print(f"Total Tests: {results.get('total_tests', 0)}")
            print(f"✅ Passed: {results.get('passed', 0)}")
            print(f"❌ Failed: {results.get('failed', 0)}")
            print(f"⏭️  Skipped: {results.get('skipped', 0)}")
            
            if results.get('summary'):
                print(f"Success Rate: {results['summary'].get('success_rate', 0):.1f}%")
                print(f"Overall Result: {results['summary'].get('overall_result', 'UNKNOWN')}")
            
            print("="*80)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error reading results file: {e}")
            return 1


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="SPX_V1 Testing Framework - Command Line Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                           # Run all tests
  python run_tests.py --category data           # Run data management tests only
  python run_tests.py --markers "unit and not slow"  # Run unit tests, exclude slow tests
  python run_tests.py --verbose --coverage      # Run with verbose output and coverage
  python run_tests.py --report-only             # Generate report from last run
        """
    )
    
    parser.add_argument(
        '--category',
        choices=['data', 'parameters', 'trading', 'risk', 'costs', 'analytics', 
                'edge_cases', 'integration', 'performance', 'compliance', 'ui'],
        help='Run tests for specific category'
    )
    
    parser.add_argument(
        '--markers',
        help='Run tests with specific markers (e.g., "unit and not slow")'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate report from last test run without running tests'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.report_only:
        return runner.generate_report_only()
    else:
        return runner.run_tests(args)


if __name__ == '__main__':
    sys.exit(main())