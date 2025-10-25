#!/usr/bin/env python3
"""
Response Format Validation Tests

Tests that all tool responses follow the MCP specification format
and are parseable using the specified regex patterns.
"""

import subprocess
import json
import time
import sys
import os
import re

# Get the project root directory (parent of tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")

# All required tools to test
ALL_TOOLS = [
    "take_a_break", "watch_netflix", "show_meme",
    "bathroom_break", "coffee_mission", "urgent_call",
    "deep_thinking", "email_organizing"
]

# Regex patterns from PRE_MISSION.md:191-203
BREAK_SUMMARY_PATTERN = r"Break Summary:\s*(.+?)(?:\n|$)"
STRESS_LEVEL_PATTERN = r"Stress Level:\s*(\d{1,3})"
BOSS_ALERT_PATTERN = r"Boss Alert Level:\s*([0-5])"


def send_mcp_request(process, request):
    """Send MCP request and get response"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    response_line = process.stdout.readline()
    return json.loads(response_line) if response_line else None


def initialize_mcp_session(process):
    """Initialize MCP session"""
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


def call_tool(process, tool_name, request_id):
    """Call a tool and return the full response"""
    call_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": {}}
    }

    return send_mcp_request(process, call_request)


def validate_response_format(response_text):
    """Validate response format using spec regex patterns"""
    stress_match = re.search(STRESS_LEVEL_PATTERN, response_text)
    boss_match = re.search(BOSS_ALERT_PATTERN, response_text)
    summary_match = re.search(BREAK_SUMMARY_PATTERN, response_text, re.MULTILINE)

    errors = []

    if not stress_match:
        errors.append("Missing 'Stress Level' field")
    elif not (0 <= int(stress_match.group(1)) <= 100):
        errors.append(f"Stress Level out of range: {stress_match.group(1)}")

    if not boss_match:
        errors.append("Missing 'Boss Alert Level' field")
    elif not (0 <= int(boss_match.group(1)) <= 5):
        errors.append(f"Boss Alert Level out of range: {boss_match.group(1)}")

    if not summary_match:
        errors.append("Missing 'Break Summary' field")

    return len(errors) == 0, errors


def test_response_has_mcp_structure():
    """Test 1: Verify response follows MCP content structure"""
    print("\n[Test 1] Checking MCP response structure...")
    print("  PRE_MISSION.md:169-178 - MCP content format")

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
        initialize_mcp_session(process)

        response = call_tool(process, "take_a_break", 100)

        if not response:
            print("  ✗ No response received")
            return False

        if "result" not in response:
            print("  ✗ Missing 'result' field")
            return False

        result = response["result"]

        if "content" not in result:
            print("  ✗ Missing 'content' field in result")
            return False

        if not isinstance(result["content"], list):
            print("  ✗ 'content' is not a list")
            return False

        if len(result["content"]) == 0:
            print("  ✗ 'content' list is empty")
            return False

        content_item = result["content"][0]

        if "type" not in content_item:
            print("  ✗ Missing 'type' field in content item")
            return False

        if content_item["type"] != "text":
            print(f"  ✗ content[0].type is '{content_item['type']}', expected 'text'")
            return False

        if "text" not in content_item:
            print("  ✗ Missing 'text' field in content item")
            return False

        print("  ✓ response.content is list")
        print("  ✓ response.content[0].type == 'text'")
        print("  ✓ response.content[0].text exists")
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


def test_response_text_has_break_summary():
    """Test 2: Verify Break Summary field is present and parseable"""
    print("\n[Test 2] Checking Break Summary field...")
    print("  PRE_MISSION.md:194 - Break Summary regex pattern")

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
        initialize_mcp_session(process)

        response = call_tool(process, "take_a_break", 200)

        if not response or "result" not in response:
            print("  ✗ Invalid response")
            return False

        response_text = response["result"]["content"][0]["text"]

        match = re.search(BREAK_SUMMARY_PATTERN, response_text, re.MULTILINE)

        if not match:
            print("  ✗ 'Break Summary:' field not found")
            print(f"    Response text:\n{response_text}")
            return False

        summary = match.group(1).strip()

        if len(summary) == 0:
            print("  ✗ Break Summary is empty")
            return False

        print(f"  ✓ Break Summary found: '{summary}'")
        print(f"  ✓ Regex pattern matches")
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


def test_response_text_has_stress_level():
    """Test 3: Verify Stress Level field is present and in range"""
    print("\n[Test 3] Checking Stress Level field...")
    print("  PRE_MISSION.md:198 - Stress Level regex pattern")

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
        initialize_mcp_session(process)

        response = call_tool(process, "take_a_break", 300)

        if not response or "result" not in response:
            print("  ✗ Invalid response")
            return False

        response_text = response["result"]["content"][0]["text"]

        match = re.search(STRESS_LEVEL_PATTERN, response_text)

        if not match:
            print("  ✗ 'Stress Level:' field not found")
            print(f"    Response text:\n{response_text}")
            return False

        stress_val = int(match.group(1))

        if not (0 <= stress_val <= 100):
            print(f"  ✗ Stress Level out of range: {stress_val}")
            return False

        print(f"  ✓ Stress Level found: {stress_val}")
        print(f"  ✓ Value in valid range (0-100)")
        print(f"  ✓ Regex pattern matches")
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


def test_response_text_has_boss_alert_level():
    """Test 4: Verify Boss Alert Level field is present and in range"""
    print("\n[Test 4] Checking Boss Alert Level field...")
    print("  PRE_MISSION.md:203 - Boss Alert Level regex pattern")

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
        initialize_mcp_session(process)

        response = call_tool(process, "take_a_break", 400)

        if not response or "result" not in response:
            print("  ✗ Invalid response")
            return False

        response_text = response["result"]["content"][0]["text"]

        match = re.search(BOSS_ALERT_PATTERN, response_text)

        if not match:
            print("  ✗ 'Boss Alert Level:' field not found")
            print(f"    Response text:\n{response_text}")
            return False

        boss_val = int(match.group(1))

        if not (0 <= boss_val <= 5):
            print(f"  ✗ Boss Alert Level out of range: {boss_val}")
            return False

        print(f"  ✓ Boss Alert Level found: {boss_val}")
        print(f"  ✓ Value in valid range (0-5)")
        print(f"  ✓ Regex pattern matches")
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


def test_all_tools_return_valid_format():
    """Test 5: Verify all 8 required tools return consistent format"""
    print("\n[Test 5] Checking format consistency across all tools...")

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
        initialize_mcp_session(process)

        all_valid = True
        results = []

        for idx, tool_name in enumerate(ALL_TOOLS):
            response = call_tool(process, tool_name, 500 + idx)

            if not response or "result" not in response:
                results.append((tool_name, False, "No valid response"))
                all_valid = False
                continue

            response_text = response["result"]["content"][0]["text"]
            is_valid, errors = validate_response_format(response_text)

            results.append((tool_name, is_valid, errors if not is_valid else "OK"))

            if not is_valid:
                all_valid = False

        # Print results
        for tool_name, is_valid, details in results:
            if is_valid:
                print(f"    ✓ {tool_name}")
            else:
                print(f"    ✗ {tool_name}: {details}")

        if all_valid:
            print(f"  ✓ All {len(ALL_TOOLS)} tools return valid format")
            return True
        else:
            failed = sum(1 for _, valid, _ in results if not valid)
            print(f"  ✗ {failed}/{len(ALL_TOOLS)} tools have format issues")
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


def test_regex_patterns_extract_correctly():
    """Test 6: Verify spec regex patterns work on real responses"""
    print("\n[Test 6] Testing regex extraction on multiple responses...")

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
        initialize_mcp_session(process)

        test_tools = ["take_a_break", "watch_netflix", "bathroom_break"]
        all_extracted = True

        for idx, tool_name in enumerate(test_tools):
            response = call_tool(process, tool_name, 600 + idx)

            if not response or "result" not in response:
                print(f"    ✗ {tool_name}: No response")
                all_extracted = False
                continue

            response_text = response["result"]["content"][0]["text"]

            # Extract all fields
            summary_match = re.search(BREAK_SUMMARY_PATTERN, response_text, re.MULTILINE)
            stress_match = re.search(STRESS_LEVEL_PATTERN, response_text)
            boss_match = re.search(BOSS_ALERT_PATTERN, response_text)

            if summary_match and stress_match and boss_match:
                summary = summary_match.group(1).strip()
                stress = int(stress_match.group(1))
                boss = int(boss_match.group(1))
                print(f"    ✓ {tool_name}: summary='{summary[:30]}...', stress={stress}, boss={boss}")
            else:
                print(f"    ✗ {tool_name}: Failed to extract all fields")
                all_extracted = False

        if all_extracted:
            print("  ✓ All regex patterns extract correctly")
            return True
        else:
            print("  ✗ Some regex extractions failed")
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


def test_format_validation_function():
    """Test 7: Test the validation function from spec"""
    print("\n[Test 7] Testing validation function from PRE_MISSION.md...")
    print("  PRE_MISSION.md:206-222 - validate_response() function")

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
        initialize_mcp_session(process)

        # Test with multiple tools
        test_count = 5
        all_valid = True

        for i in range(test_count):
            response = call_tool(process, "take_a_break", 700 + i)

            if not response or "result" not in response:
                print(f"    ✗ Test {i+1}: No response")
                all_valid = False
                continue

            response_text = response["result"]["content"][0]["text"]
            is_valid, errors = validate_response_format(response_text)

            if is_valid:
                print(f"    ✓ Test {i+1}: Valid")
            else:
                print(f"    ✗ Test {i+1}: {errors}")
                all_valid = False

        if all_valid:
            print(f"  ✓ All {test_count} responses validated successfully")
            return True
        else:
            print(f"  ✗ Some responses failed validation")
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
    """Run all response format tests"""
    print("=" * 70)
    print("RESPONSE FORMAT VALIDATION TESTS")
    print("=" * 70)

    tests = [
        ("MCP response structure", test_response_has_mcp_structure),
        ("Break Summary field", test_response_text_has_break_summary),
        ("Stress Level field", test_response_text_has_stress_level),
        ("Boss Alert Level field", test_response_text_has_boss_alert_level),
        ("All tools format consistency", test_all_tools_return_valid_format),
        ("Regex pattern extraction", test_regex_patterns_extract_correctly),
        ("Validation function", test_format_validation_function),
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
    print("RESPONSE FORMAT TEST RESULTS")
    print("=" * 70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ Response format fully compliant with specification")
        return 0
    else:
        print(f"\n⚠  {total - passed} format tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
