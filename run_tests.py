#!/usr/bin/env python3
"""Script to run tests for the knowledge assistant."""

import subprocess
import sys
import os


def run_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running AI Personal Knowledge Assistant Tests")
    print("=" * 50)
    
    # Run agent tests
    print("\n1. Running Agent Tests...")
    result = subprocess.run(
        [sys.executable, "tests/test_agents.py"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("❌ Agent tests failed!")
        return False
    
    print("✓ Agent tests passed!")
    
    # Run pytest if available
    print("\n2. Running Pytest Tests...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print("❌ Pytest tests failed!")
            return False
        
        print("✓ Pytest tests passed!")
        
    except Exception as e:
        print(f"⚠️  Pytest not available: {e}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully! ✓")
    print("=" * 50)
    
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)