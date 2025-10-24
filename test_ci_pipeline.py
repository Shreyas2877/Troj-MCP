#!/usr/bin/env python3
"""
Test script to verify CI/CD pipeline functionality.
This script can be used to test the pipeline locally or trigger it.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def test_linting():
    """Test linting tools."""
    print("\n📝 Testing Linting...")
    success = True

    # Test ruff
    success &= run_command("ruff check .", "Ruff linting")

    # Test black
    success &= run_command("black --check .", "Black formatting")

    return success


def test_tests():
    """Test running the test suite."""
    print("\n🧪 Testing Test Suite...")
    return run_command("python -m pytest tests/ -v", "Running tests")


def test_coverage():
    """Test coverage reporting."""
    print("\n📊 Testing Coverage...")
    return run_command(
        "python -m pytest tests/ --cov=src/macro_man --cov-report=term",
        "Coverage report",
    )


def test_docker_build():
    """Test Docker build locally."""
    print("\n🐳 Testing Docker Build...")
    return run_command("docker build -t troj-mcp:test .", "Docker build")


def main():
    """Run all CI/CD pipeline tests."""
    print("🚀 Troj-MCP CI/CD Pipeline Test")
    print("===============================")

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: Not in Troj-MCP project directory")
        sys.exit(1)

    # Check if virtual environment is activated
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Warning: Virtual environment not detected")
        print("Consider running: source venv/bin/activate")

    all_success = True

    # Run all tests
    all_success &= test_linting()
    all_success &= test_tests()
    all_success &= test_coverage()
    all_success &= test_docker_build()

    print("\n" + "=" * 50)
    if all_success:
        print("🎉 All CI/CD pipeline tests PASSED!")
        print("✅ Your code is ready for the v1.0.0 release branch")
    else:
        print("❌ Some CI/CD pipeline tests FAILED!")
        print("🔧 Please fix the issues before pushing to v1.0.0")
        sys.exit(1)


if __name__ == "__main__":
    main()
