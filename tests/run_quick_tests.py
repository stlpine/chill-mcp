#!/usr/bin/env python3
"""
ChillMCP Quick Test Runner (for CI/CD pipelines)

Executes essential test suites quickly for rapid feedback during development.
Uses simplified versions of tests where appropriate to minimize execution time.

Target runtime: <30 seconds
Recommended for: CI/CD, pull requests, rapid development iteration

For comprehensive validation before submission, use run_all_tests.py
"""

import subprocess
import sys
import os
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable

# Quick test suites - optimized for speed
QUICK_TEST_SUITES = [
    {
        "name": "CLI Parameters",
        "file": "test_cli_parameters.py",
        "critical": True,
        "weight": "REQUIRED",
        "description": "Command-line parameter support (auto-fail gate)"
    },
    {
        "name": "MCP Protocol",
        "file": "test_mcp_protocol.py",
        "critical": False,
        "weight": "Foundation",
        "description": "MCP server basic operation"
    },
    {
        "name": "State Management (Quick)",
        "file": "simple_state_test.py",
        "critical": False,
        "weight": "30%",
        "description": "Core state logic (fast version, ~10s)"
    },
    {
        "name": "Response Format",
        "file": "test_response_format.py",
        "critical": False,
        "weight": "Required",
        "description": "Response format validation"
    }
]


def print_banner(text, char="="):
    """Print a banner with text"""
    width = 70
    print(char * width)
    print(text.center(width))
    print(char * width)


def print_section(text, char="─"):
    """Print a section separator"""
    print("\n" + char * 70)
    print(text)
    print(char * 70)


def run_test_suite(suite_info, index, total):
    """Run a single test suite and return results"""
    name = suite_info["name"]
    file = suite_info["file"]
    critical = suite_info["critical"]
    weight = suite_info["weight"]
    description = suite_info["description"]

    print_section(f"[{index}/{total}] {name} ({weight})")
    print(f"Description: {description}")

    if critical:
        print("⚠️  CRITICAL GATE - Failure will stop all testing")

    print()

    # Run the test
    test_path = os.path.join(PROJECT_ROOT, "tests", file)

    try:
        result = subprocess.run(
            [PYTHON_PATH, test_path],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per test
        )

        # Print output
        print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        # Parse result
        passed = result.returncode == 0

        return {
            "name": name,
            "passed": passed,
            "critical": critical,
            "weight": weight,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        print(f"✗ Test suite timed out after 2 minutes")
        return {
            "name": name,
            "passed": False,
            "critical": critical,
            "weight": weight,
            "returncode": -1
        }
    except Exception as e:
        print(f"✗ Error running test suite: {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": name,
            "passed": False,
            "critical": critical,
            "weight": weight,
            "returncode": -1
        }


def print_summary(results):
    """Print final summary"""
    print_banner("QUICK TEST RESULTS", "=")

    print("\nTest Suite Results:")
    print("─" * 70)

    all_passed = True
    critical_failed = False

    for result in results:
        name = result["name"]
        passed = result["passed"]
        critical = result["critical"]
        weight = result["weight"]

        if passed:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
            all_passed = False
            if critical:
                critical_failed = True

        critical_marker = " ⚠️ CRITICAL" if critical else ""
        print(f"{status:8s} | {name:30s} ({weight:12s}){critical_marker}")

    print("─" * 70)

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} test suites passed")

    if critical_failed:
        print("\n⚠️  CRITICAL GATE FAILED")
        print("CLI parameters not working correctly.")
        print("Per PRE_MISSION.md:279-285, this is an AUTO-FAIL.")
        return False

    if all_passed:
        print("\n" + "=" * 70)
        print("✓ ALL QUICK TESTS PASSED!")
        print("=" * 70)
        print("\nNote: This is the QUICK test suite for rapid feedback.")
        print("Before submission, run: python tests/run_all_tests.py")
        print("Full suite includes:")
        print("  - Comprehensive state management tests (~3 min)")
        print("  - Integration scenarios")
        print("  - Time-based mechanic validation")
        return True
    else:
        print("\n" + "=" * 70)
        print("✗ SOME QUICK TESTS FAILED")
        print("=" * 70)
        print("\nPlease fix the failures above before continuing.")
        return False


def main():
    """Run quick test suites"""
    start_time = datetime.now()

    print_banner("ChillMCP Quick Test Suite (CI/CD)", "=")
    print(f"\nStarting quick test run at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test suites: {len(QUICK_TEST_SUITES)}")
    print(f"Target runtime: <30 seconds")
    print()

    results = []

    for index, suite in enumerate(QUICK_TEST_SUITES, 1):
        result = run_test_suite(suite, index, len(QUICK_TEST_SUITES))
        results.append(result)

        # If critical test failed, stop immediately
        if result["critical"] and not result["passed"]:
            print("\n" + "!" * 70)
            print("CRITICAL GATE FAILURE - STOPPING ALL TESTS")
            print("!" * 70)
            print("\nPer PRE_MISSION.md:279-285, CLI parameter support is REQUIRED.")
            print("Fix CLI parameters before running other tests.")
            break

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n\nQuick test run completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration:.1f} seconds")

    success = print_summary(results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
