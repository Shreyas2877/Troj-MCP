#!/usr/bin/env python3
"""
Test runner for Macro-Man MCP Server.
Run this script to execute all available tests.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🧪 {description}...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Macro-Man MCP Server Test Suite")
    print("=" * 50)
    
    # Set environment variables
    os.environ["SECRET_KEY"] = "test-key-for-testing"
    
    tests = [
        {
            "cmd": ["python", "-m", "pytest", "tests/test_components.py", "-v"],
            "description": "Component Tests"
        },
        {
            "cmd": ["python", "test_manual.py"],
            "description": "Manual Integration Tests"
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if run_command(test["cmd"], test["description"]):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
