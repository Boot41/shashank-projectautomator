#!/usr/bin/env python3
"""
Comprehensive test runner for the fastmcp project.
This script provides various options for running tests with different configurations.
"""
import sys
import subprocess
import os
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"Command timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_unit_tests():
    """Run all unit tests."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/unit/", 
        "-v", 
        "--tb=short",
        "--no-header"
    ]
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests():
    """Run all integration tests."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/integration/", 
        "-v", 
        "--tb=short",
        "--no-header"
    ]
    return run_command(cmd, "Running Integration Tests")


def run_all_tests():
    """Run all tests."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/", 
        "-v", 
        "--tb=short",
        "--no-header"
    ]
    return run_command(cmd, "Running All Tests")


def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/", 
        "-v", 
        "--tb=short",
        "--no-header",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=70",
        "--cov-branch"
    ]
    return run_command(cmd, "Running Tests with Coverage")


def run_specific_test(test_file):
    """Run a specific test file."""
    cmd = [
        sys.executable, "-m", "pytest", 
        f"test/{test_file}", 
        "-v", 
        "--tb=short",
        "--no-header"
    ]
    return run_command(cmd, f"Running {test_file}")


def run_tests_by_marker(marker):
    """Run tests by marker."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/", 
        "-v", 
        "--tb=short",
        "--no-header",
        f"-m {marker}"
    ]
    return run_command(cmd, f"Running Tests with marker: {marker}")


def run_linting():
    """Run code linting."""
    cmd = [
        sys.executable, "-m", "flake8", 
        "app/", 
        "--max-line-length=100",
        "--ignore=E203,W503"
    ]
    return run_command(cmd, "Running Code Linting")


def run_formatting():
    """Run code formatting."""
    cmd = [
        sys.executable, "-m", "black", 
        "app/", 
        "--line-length=100"
    ]
    return run_command(cmd, "Running Code Formatting")


def run_import_sorting():
    """Run import sorting."""
    cmd = [
        sys.executable, "-m", "isort", 
        "app/", 
        "--profile=black"
    ]
    return run_command(cmd, "Running Import Sorting")


def install_test_dependencies():
    """Install test dependencies."""
    cmd = [
        sys.executable, "-m", "pip", 
        "install", 
        "-r", "requirements.txt"
    ]
    return run_command(cmd, "Installing Dependencies")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test runner for fastmcp project")
    parser.add_argument("command", choices=[
        "install", "unit", "integration", "all", "coverage", 
        "lint", "format", "sort", "specific"
    ], help="Command to run")
    parser.add_argument("--test-path", help="Path to specific test file (for 'specific' command)")
    parser.add_argument("--no-install", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = True
    
    if not args.no_install and args.command != "install":
        print("Installing dependencies...")
        success = install_test_dependencies()
        if not success:
            print("Failed to install dependencies")
            return 1
    
    if args.command == "install":
        success = install_test_dependencies()
    elif args.command == "unit":
        success = run_unit_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "coverage":
        success = run_tests_with_coverage()
    elif args.command == "lint":
        success = run_linting()
    elif args.command == "format":
        success = run_formatting()
    elif args.command == "sort":
        success = run_import_sorting()
    elif args.command == "specific":
        if not args.test_path:
            print("Error: --test-path is required for 'specific' command")
            return 1
        success = run_specific_test(args.test_path)
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All operations completed successfully!")
        print(f"{'='*60}")
        return 0
    else:
        print(f"\n{'='*60}")
        print("❌ Some operations failed!")
        print(f"{'='*60}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
