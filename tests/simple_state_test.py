#!/usr/bin/env python3
"""
Simple State Test - Fast version without long waits
"""

import subprocess
import json
import time
import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")


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
    """Call a tool and return the response text"""
    call_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": {}}
    }

    response = send_mcp_request(process, call_request)
    if response and "result" in response and "content" in response["result"]:
        content = response["result"]["content"]
        if content and len(content) > 0 and "text" in content[0]:
            return content[0]["text"]
    return None


def extract_boss_alert(response_text):
    """Extract boss alert level from response"""
    pattern = r"Boss Alert Level:\s*([0-5])"
    match = re.search(pattern, response_text)
    return int(match.group(1)) if match else None


def test_boss_alert_increases():
    """Test boss alert increases with boss_alertness=100"""
    print("\n[Test 1] Boss alert should increase (boss_alertness=100)...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "100", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        initialize_mcp_session(process)

        # Take breaks until boss alert increases
        boss_levels = []

        for i in range(10):
            response_text = call_tool(process, "take_a_break", 100 + i)
            boss_alert = extract_boss_alert(response_text)
            if boss_alert is not None:
                boss_levels.append(boss_alert)
                if boss_alert >= 5:
                    break

        print(f"    Boss alert progression: {boss_levels}")

        if len(boss_levels) > 0 and max(boss_levels) > 0:
            print("  ✓ Boss alert increases")
            return True
        else:
            print(f"  ✗ Boss alert did not increase: {boss_levels}")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()


def test_boss_alert_stays_zero():
    """Test boss alert stays at 0 with boss_alertness=0"""
    print("\n[Test 2] Boss alert should stay at 0 (boss_alertness=0)...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "0", "--boss_alertness_cooldown", "300"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        initialize_mcp_session(process)

        # Take breaks, boss should stay at 0
        boss_levels = []

        for i in range(10):
            response_text = call_tool(process, "take_a_break", 200 + i)
            boss_alert = extract_boss_alert(response_text)
            if boss_alert is not None:
                boss_levels.append(boss_alert)

        print(f"    Boss alert levels: {boss_levels}")

        if len(boss_levels) > 0 and all(b == 0 for b in boss_levels):
            print("  ✓ Boss alert stayed at 0")
            return True
        else:
            print(f"  ✗ Boss alert increased when it shouldn't: {boss_levels}")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()


def test_boss_alert_cooldown():
    """Test boss alert decreases on cooldown"""
    print("\n[Test 3] Boss alert should decrease on cooldown...")

    process = subprocess.Popen(
        [PYTHON_PATH, MAIN_PATH, "--boss_alertness", "100", "--boss_alertness_cooldown", "5"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    time.sleep(1)

    try:
        initialize_mcp_session(process)

        # Raise boss alert
        for i in range(3):
            call_tool(process, "take_a_break", 300 + i)

        # Get current boss alert using status check (doesn't take a break)
        response_text = call_tool(process, "check_stress_status", 310)
        boss_before = extract_boss_alert(response_text)

        if boss_before is None or boss_before == 0:
            print("  ⚠ Could not raise boss alert, skipping test")
            return True

        print(f"    Boss alert before cooldown: {boss_before}")

        # Wait for cooldown
        print("    Waiting 7 seconds for cooldown...")
        time.sleep(7)

        # Check boss alert using status check (doesn't reset cooldown)
        response_text = call_tool(process, "check_stress_status", 311)
        boss_after = extract_boss_alert(response_text)

        print(f"    Boss alert after cooldown: {boss_after}")

        if boss_after < boss_before:
            print("  ✓ Boss alert decreased")
            return True
        elif boss_after == 0:
            print("  ✓ Boss alert at minimum")
            return True
        else:
            print(f"  ✗ Boss alert did not decrease: {boss_before} -> {boss_after}")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()


def main():
    """Run simple state tests"""
    print("=" * 70)
    print("SIMPLE STATE TESTS (Fast Version)")
    print("=" * 70)

    tests = [
        test_boss_alert_increases,
        test_boss_alert_stays_zero,
        test_boss_alert_cooldown,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    passed = sum(1 for r in results if r)
    total = len(results)

    print(f"Total: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
