#!/usr/bin/env python3
"""
Test runner for the Smart Kitchen Queue Management System.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Smart Kitchen Queue Management System")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ["PYTHONPATH"] = str(Path.cwd())
    
    # Base pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.fast:
        pytest_cmd += " -m 'not slow'"
    
    # Determine which tests to run
    test_files = []
    
    if args.unit:
        test_files.extend([
            "tests/test_excel_service.py",
            "tests/test_queue_manager.py",
            "tests/test_starvation_prevention.py"
        ])
    elif args.integration:
        test_files.append("tests/test_integration.py")
    elif args.api:
        test_files.append("tests/test_api.py")
    elif args.performance:
        test_files.append("tests/test_performance.py")
    else:
        # Run all tests
        test_files = [
            "tests/test_excel_service.py",
            "tests/test_queue_manager.py", 
            "tests/test_starvation_prevention.py",
            "tests/test_integration.py",
            "tests/test_api.py"
        ]
        
        if not args.fast:
            test_files.append("tests/test_performance.py")
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    # Run tests
    success = True
    
    print("🚀 Starting Smart Kitchen Queue Management System Tests")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Install dependencies first
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return 1
    
    # Run linting (optional)
    if not args.fast:
        print("\n📋 Running code quality checks...")
        
        # Check if flake8 is available
        try:
            subprocess.run(["flake8", "--version"], capture_output=True, check=True)
            run_command("flake8 app --max-line-length=100 --ignore=E203,W503", "Code linting (flake8)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  flake8 not available, skipping linting")
    
    # Run the tests
    for test_file in test_files:
        if os.path.exists(test_file):
            cmd = f"{pytest_cmd} {test_file}"
            if not run_command(cmd, f"Running {test_file}"):
                success = False
        else:
            print(f"⚠️  Test file {test_file} not found, skipping")
    
    # Generate final report
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    if success:
        print("✅ All tests passed successfully!")
        
        if args.coverage:
            print("\n📈 Coverage report generated in htmlcov/index.html")
        
        print("\n🎉 Smart Kitchen Queue Management System is ready for deployment!")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
