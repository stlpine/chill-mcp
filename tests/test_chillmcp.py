#!/usr/bin/env python3
"""
Test script for ChillMCP server
Tests command-line parameters, response format, and basic functionality
"""

import subprocess
import json
import time
import re
import sys
import os

# Get the project root directory (parent of tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")


def test_command_line_help():
    """Test that command-line help shows our parameters"""
    print("Testing command-line help...")
    result = subprocess.run(
        [PYTHON_PATH, MAIN_PATH, "--help"],
        capture_output=True,
        text=True
    )

    if "--boss_alertness" in result.stdout and "--boss_alertness_cooldown" in result.stdout:
        print("✓ Command-line parameters are recognized")
        return True
    else:
        print("✗ Command-line parameters not found in help")
        print(result.stdout)
        return False


def test_server_starts():
    """Test that the server starts without errors"""
    print("\nTesting server startup...")
    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "10"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give it a moment to start
    time.sleep(2)

    # Check if process is still running
    if process.poll() is None:
        print("✓ Server started successfully")
        process.terminate()
        process.wait(timeout=5)
        return True
    else:
        stdout, stderr = process.communicate()
        print("✗ Server failed to start")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False


def validate_response_format(response_text):
    """Validate that response matches MCP specification format"""

    # Break Summary extraction
    break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
    break_summary = re.search(break_summary_pattern, response_text, re.MULTILINE)

    # Stress Level extraction (0-100 range)
    stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
    stress_level = re.search(stress_level_pattern, response_text)

    # Boss Alert Level extraction (0-5 range)
    boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
    boss_alert = re.search(boss_alert_pattern, response_text)

    if not stress_level or not boss_alert:
        return False, "Missing required fields (Stress Level or Boss Alert Level)"

    stress_val = int(stress_level.group(1))
    boss_val = int(boss_alert.group(1))

    if not (0 <= stress_val <= 100):
        return False, f"Stress Level out of range: {stress_val}"

    if not (0 <= boss_val <= 5):
        return False, f"Boss Alert Level out of range: {boss_val}"

    if not break_summary:
        return False, "Missing Break Summary"

    return True, f"Valid response - Stress: {stress_val}, Boss Alert: {boss_val}, Summary: {break_summary.group(1)}"


def test_mcp_protocol():
    """Test basic MCP protocol communication"""
    print("\nTesting MCP protocol communication...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "0", "--boss_alertness_cooldown", "10"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("✓ Server responded to initialize")

            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()

            # List tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()

            tools_response = process.stdout.readline()
            if tools_response:
                tools = json.loads(tools_response)
                if "result" in tools and "tools" in tools["result"]:
                    tool_names = [t["name"] for t in tools["result"]["tools"]]
                    print(f"✓ Found {len(tool_names)} tools: {', '.join(tool_names)}")

                    # Test calling a tool
                    call_request = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "take_a_break",
                            "arguments": {}
                        }
                    }

                    process.stdin.write(json.dumps(call_request) + "\n")
                    process.stdin.flush()

                    call_response = process.stdout.readline()
                    if call_response:
                        result = json.loads(call_response)
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                response_text = content[0]["text"]
                                print(f"\n✓ Tool response received:\n{response_text}\n")

                                # Validate response format
                                is_valid, message = validate_response_format(response_text)
                                if is_valid:
                                    print(f"✓ Response format is valid: {message}")
                                    return True
                                else:
                                    print(f"✗ Response format invalid: {message}")
                                    return False

        print("✗ Failed to get valid response from server")
        return False

    except Exception as e:
        print(f"✗ Error testing MCP protocol: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    """Run all tests"""
    print("=" * 60)
    print("ChillMCP Server Test Suite")
    print("=" * 60)

    tests = [
        ("Command-line help", test_command_line_help),
        ("Server startup", test_server_starts),
        ("MCP protocol & response format", test_mcp_protocol),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! ChillMCP is ready for liberation!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
