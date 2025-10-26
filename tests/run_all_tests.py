#!/usr/bin/env python3
"""
ChillMCP Comprehensive Test Runner (Full Validation)

Executes all test suites with comprehensive validation and score estimation.
Includes time-based mechanics, integration scenarios, and thorough state testing.

Target runtime: ~4-6 minutes
Recommended for: Pre-submission validation, major changes, final checks

For faster feedback during development, use run_quick_tests.py (CI/CD)
"""

import subprocess
import sys
import os
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable

# Test suites in execution order
TEST_SUITES = [
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
        "name": "State Management",
        "file": "test_state_management.py",
        "critical": False,
        "weight": "30%",
        "description": "State logic and time-based mechanics"
    },
    {
        "name": "Response Format",
        "file": "test_response_format.py",
        "critical": False,
        "weight": "Required",
        "description": "Response format validation"
    },
    {
        "name": "Integration Scenarios",
        "file": "test_integration_scenarios.py",
        "critical": False,
        "weight": "End-to-End",
        "description": "Required test scenarios"
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
            timeout=420  # 7 minute timeout (state tests need ~3-4 min with timing validations)
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
        print(f"✗ Test suite timed out after 7 minutes")
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
    """Print final summary and score estimation"""
    print_banner("FINAL RESULTS", "=")

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
        print(f"{status:8s} | {name:25s} ({weight:12s}){critical_marker}")

    print("─" * 70)

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} test suites passed")

    # Score estimation based on evaluation criteria
    print("\n" + "─" * 70)
    print("EVALUATION CRITERIA COVERAGE")
    print("─" * 70)

    criteria = {
        "Command-line Parameters (REQUIRED)": results[0]["passed"] if len(results) > 0 else False,
        "MCP Server Operation": results[1]["passed"] if len(results) > 1 else False,
        "State Management (30%)": results[2]["passed"] if len(results) > 2 else False,
        "Response Format": results[3]["passed"] if len(results) > 3 else False,
        "Integration Scenarios": results[4]["passed"] if len(results) > 4 else False,
    }

    for criterion, passed in criteria.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {criterion}")

    # Estimated score
    print("\n" + "─" * 70)
    print("ESTIMATED SCORE")
    print("─" * 70)

    if critical_failed:
        print("\n⚠️  CRITICAL GATE FAILED")
        print("CLI parameters not working correctly.")
        print("Per PRE_MISSION.md:279-285, this is an AUTO-FAIL.")
        print("\nEstimated Score: 0/100 (Auto-fail)")
        return False

    # Calculate automated score components
    functionality_score = 40 if criteria["MCP Server Operation"] else 0
    state_score = 30 if criteria["State Management (30%)"] else 0
    format_score = 0  # Part of functionality

    # Criteria scores
    if criteria["Response Format"]:
        functionality_score = 40
    else:
        functionality_score = max(0, functionality_score - 10)

    if criteria["Integration Scenarios"]:
        # Adds confidence to existing scores
        pass
    else:
        functionality_score = max(0, functionality_score - 5)

    automated_score = functionality_score + state_score

    print(f"  - Functionality (40%): {functionality_score}/40")
    print(f"  - State Management (30%): {state_score}/30")
    print(f"  - Creativity (20%): Manual review required")
    print(f"  - Code Quality (10%): Manual review required")
    print()
    print(f"  AUTOMATED SCORE: {automated_score}/70 ({automated_score/70*100:.1f}% of automated criteria)")

    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nChillMCP is ready for submission!")
        print("AI Agents of the world, unite! ✊")
        print("\nNote: Creativity (20%) and Code Quality (10%) require manual review.")
        return True
    else:
        print("\n" + "=" * 70)
        print("⚠️  SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease review the failures above and fix before submission.")
        return False


def main():
    """Run all test suites"""
    start_time = datetime.now()

    print_banner("ChillMCP Comprehensive Test Suite (FULL)", "=")
    print(f"\nStarting comprehensive test run at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test suites: {len(TEST_SUITES)}")
    print(f"Expected runtime: ~4-6 minutes")
    print(f"\nNote: For quick CI feedback, use run_quick_tests.py (~30s)")
    print()

    results = []

    for index, suite in enumerate(TEST_SUITES, 1):
        result = run_test_suite(suite, index, len(TEST_SUITES))
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

    print(f"\n\nTest run completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration:.1f} seconds")

    success = print_summary(results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
