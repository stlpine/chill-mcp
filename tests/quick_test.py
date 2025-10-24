#!/usr/bin/env python3
"""
Quick Test - Fast validation of core functionality
"""

import subprocess
import json
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PATH = sys.executable
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")


def send_mcp_request(process, request):
    """Send MCP request and get response"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    response_line = process.stdout.readline()
    return json.loads(response_line) if response_line else None


def test_basic_functionality():
    """Quick test of basic functionality"""
    print("=" * 70)
    print("QUICK FUNCTIONALITY TEST")
    print("=" * 70)

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

        # Call a simple tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "take_a_break", "arguments": {}}
        }

        response = send_mcp_request(process, call_request)

        if response and "result" in response:
            content = response["result"]["content"]
            if content and len(content) > 0 and "text" in content[0]:
                text = content[0]["text"]
                print("\n✓ MCP server responds correctly")
                print(f"\nSample response:\n{text[:200]}...")

                # Check format
                if "Stress Level:" in text and "Boss Alert Level:" in text:
                    print("✓ Response format correct")
                    return True
                else:
                    print("✗ Response format missing fields")
                    return False
        else:
            print("✗ No valid response received")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
