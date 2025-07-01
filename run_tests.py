#!/usr/bin/env python3
"""
Test runner script for JJ Pastebin.

This script provides various options for running tests locally.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"{'='*60}")
    
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str))
    
    if result.returncode == 0:
        print(f"✅ {description or 'Command'} passed")
    else:
        print(f"❌ {description or 'Command'} failed")
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="JJ Pastebin Test Runner")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "web", "auth", "cli", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--security", 
        action="store_true",
        help="Run security checks"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="Install test dependencies first"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = True
    
    # Install dependencies if requested
    if args.install_deps:
        success &= run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], "Installing requirements")
        
        success &= run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"
        ], "Installing dev requirements")
        
        success &= run_command([
            sys.executable, "-m", "pip", "install", "Werkzeug<3.0.0"
        ], "Installing compatible Werkzeug")
    
    # Create instance directory
    os.makedirs("instance", exist_ok=True)
    
    # Run linting if requested
    if args.lint:
        success &= run_command([
            "flake8", ".", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
        ], "Flake8 syntax check")
        
        success &= run_command([
            "black", "--check", "--diff", "."
        ], "Black code formatting check")
        
        success &= run_command([
            "isort", "--check-only", "--diff", "."
        ], "Import sorting check")
    
    # Run security checks if requested
    if args.security:
        success &= run_command([
            "bandit", "-r", "app/", "cli/", "-ll"
        ], "Security check with Bandit")
        
        success &= run_command([
            "safety", "check"
        ], "Dependency security check")
    
    # Build pytest command
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.coverage:
        pytest_cmd.extend([
            "--cov=app", 
            "--cov=cli", 
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add test type markers
    if args.type != "all":
        if args.type == "unit":
            pytest_cmd.extend(['-m', 'not integration'])
        elif args.type == "integration":
            pytest_cmd.extend(['-m', 'integration'])
        else:
            pytest_cmd.extend(['-m', args.type])
    
    # Set environment variables for testing
    env = os.environ.copy()
    env.update({
        'FLASK_ENV': 'testing',
        'DATABASE_URL': 'sqlite:///:memory:',
        'TESTING': 'true'
    })
    
    # Run tests
    success &= run_command(
        pytest_cmd,
        f"Running {args.type} tests" + (" with coverage" if args.coverage else "")
    )
    
    # Final report
    print(f"\n{'='*60}")
    if success:
        print("🎉 All checks passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("💥 Some checks failed!")
        sys.exit(1)
    print(f"{'='*60}")


if __name__ == "__main__":
    main() 