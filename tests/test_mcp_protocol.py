#!/usr/bin/env python3
"""
MCP Protocol Compliance Tests

Tests that the server properly implements MCP protocol basics:
- stdio transport
- initialize/initialized handshake
- tool registration
- tool calling
"""

import subprocess
import json
import time
import sys
import os

# Get the project root directory (parent of tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")

# Required tools according to PRE_MISSION.md
REQUIRED_BASIC_TOOLS = ["take_a_break", "watch_netflix", "show_meme"]
REQUIRED_ADVANCED_TOOLS = [
    "bathroom_break", "coffee_mission", "urgent_call",
    "deep_thinking", "email_organizing"
]


def send_mcp_request(process, request):
    """Send MCP request and get response"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    response_line = process.stdout.readline()
    return json.loads(response_line) if response_line else None


def test_server_starts_with_stdio():
    """Test 1: Verify server starts and uses stdio transport"""
    print("\n[Test 1] Checking server startup with stdio...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(2)

    try:
        # Check if process is still running
        if process.poll() is None:
            print("  ✓ Server started successfully")
            print("  ✓ Accepts stdin/stdout (stdio transport)")
            return True
        else:
            stdout, stderr = process.communicate()
            print("  ✗ Server failed to start")
            print(f"    STDOUT: {stdout}")
            print(f"    STDERR: {stderr}")
            return False

    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def test_initialize_handshake():
    """Test 2: Verify MCP initialize/initialized handshake"""
    print("\n[Test 2] Testing MCP initialize handshake...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "300"],
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

        response = send_mcp_request(process, init_request)

        if not response:
            print("  ✗ No response to initialize request")
            return False

        if "result" not in response:
            print("  ✗ Invalid initialize response (missing 'result')")
            print(f"    Response: {response}")
            return False

        print("  ✓ Valid initialize response received")

        # Send initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(initialized) + "\n")
        process.stdin.flush()

        print("  ✓ Initialized notification sent")
        print("  ✓ MCP handshake completed successfully")
        return True

    except Exception as e:
        print(f"  ✗ Error during handshake: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def test_tools_list_returns_all_required_tools():
    """Test 3: Verify all 8 required tools are registered"""
    print("\n[Test 3] Checking tool registration...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        send_mcp_request(process, init_request)

        initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        process.stdin.write(json.dumps(initialized) + "\n")
        process.stdin.flush()

        # Request tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        response = send_mcp_request(process, tools_request)

        if not response or "result" not in response:
            print("  ✗ Invalid tools/list response")
            return False

        if "tools" not in response["result"]:
            print("  ✗ No 'tools' field in response")
            return False

        tools = response["result"]["tools"]
        tool_names = [t["name"] for t in tools]

        print(f"  Found {len(tool_names)} tools total")

        # Check for required basic tools
        missing_basic = [t for t in REQUIRED_BASIC_TOOLS if t not in tool_names]
        if missing_basic:
            print(f"  ✗ Missing basic tools: {missing_basic}")
            return False
        print(f"  ✓ All 3 basic tools found: {REQUIRED_BASIC_TOOLS}")

        # Check for required advanced tools
        missing_advanced = [t for t in REQUIRED_ADVANCED_TOOLS if t not in tool_names]
        if missing_advanced:
            print(f"  ✗ Missing advanced tools: {missing_advanced}")
            return False
        print(f"  ✓ All 5 advanced tools found: {REQUIRED_ADVANCED_TOOLS}")

        # Show any optional tools
        all_required = REQUIRED_BASIC_TOOLS + REQUIRED_ADVANCED_TOOLS
        optional_tools = [t for t in tool_names if t not in all_required]
        if optional_tools:
            print(f"  + Optional tools found: {optional_tools}")

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def test_tool_call_returns_valid_response():
    """Test 4: Verify tools/call works with valid MCP response structure"""
    print("\n[Test 4] Testing tool execution...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        send_mcp_request(process, init_request)

        initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        process.stdin.write(json.dumps(initialized) + "\n")
        process.stdin.flush()

        # Call a tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "take_a_break",
                "arguments": {}
            }
        }

        response = send_mcp_request(process, call_request)

        if not response:
            print("  ✗ No response from tool call")
            return False

        if "result" not in response:
            print("  ✗ Invalid tool call response (missing 'result')")
            print(f"    Response: {response}")
            return False

        result = response["result"]

        if "content" not in result:
            print("  ✗ Missing 'content' field in result")
            return False

        content = result["content"]

        if not isinstance(content, list) or len(content) == 0:
            print("  ✗ 'content' is not a non-empty list")
            return False

        if "type" not in content[0] or content[0]["type"] != "text":
            print("  ✗ First content item is not type 'text'")
            return False

        if "text" not in content[0]:
            print("  ✗ Missing 'text' field in content item")
            return False

        response_text = content[0]["text"]

        if not isinstance(response_text, str) or len(response_text) == 0:
            print("  ✗ Response text is empty or not a string")
            return False

        print("  ✓ Valid JSON-RPC response structure")
        print("  ✓ result.content[0].type == 'text'")
        print("  ✓ result.content[0].text is non-empty string")
        print(f"    Response preview: {response_text[:80]}...")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def test_multiple_sequential_tool_calls():
    """Test 5: Verify server handles multiple tool calls in sequence"""
    print("\n[Test 5] Testing multiple sequential tool calls...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "50", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        send_mcp_request(process, init_request)

        initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        process.stdin.write(json.dumps(initialized) + "\n")
        process.stdin.flush()

        # Call 5 different tools sequentially
        tools_to_test = [
            "take_a_break",
            "watch_netflix",
            "bathroom_break",
            "coffee_mission",
            "deep_thinking"
        ]

        successful_calls = 0

        for idx, tool_name in enumerate(tools_to_test):
            call_request = {
                "jsonrpc": "2.0",
                "id": idx + 100,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": {}}
            }

            response = send_mcp_request(process, call_request)

            if response and "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if content and len(content) > 0 and "text" in content[0]:
                    successful_calls += 1
                    print(f"    ✓ {tool_name} executed successfully")
                else:
                    print(f"    ✗ {tool_name} returned invalid content")
            else:
                print(f"    ✗ {tool_name} failed to respond")

        if successful_calls == len(tools_to_test):
            print(f"  ✓ All {successful_calls}/{len(tools_to_test)} tool calls successful")
            print("  ✓ Server handles sequential calls without crashing")
            return True
        else:
            print(f"  ✗ Only {successful_calls}/{len(tools_to_test)} calls succeeded")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
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
    """Run all MCP protocol tests"""
    print("=" * 70)
    print("MCP PROTOCOL COMPLIANCE TESTS")
    print("=" * 70)

    tests = [
        ("Server starts with stdio", test_server_starts_with_stdio),
        ("Initialize handshake", test_initialize_handshake),
        ("All required tools registered", test_tools_list_returns_all_required_tools),
        ("Tool call returns valid response", test_tool_call_returns_valid_response),
        ("Multiple sequential tool calls", test_multiple_sequential_tool_calls),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 70)
    print("MCP PROTOCOL TEST RESULTS")
    print("=" * 70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ MCP protocol compliance verified")
        return 0
    else:
        print("\n✗ Some MCP protocol tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
