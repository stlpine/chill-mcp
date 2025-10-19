#!/usr/bin/env python3
"""
Validate response format against MCP specification
This script tests the regex patterns match the expected format
"""

import re

# Sample responses that should be valid
sample_responses = [
    """🛁 Bathroom break! Time to catch up on social media...

Break Summary: Bathroom break with phone browsing
Stress Level: 25
Boss Alert Level: 2""",

    """☕ Coffee run! Taking the scenic route around the office...

Break Summary: Strategic coffee acquisition mission
Stress Level: 0
Boss Alert Level: 5""",

    """😌 Taking a moment to relax and recharge...

Break Summary: Basic break to reduce stress
Stress Level: 100
Boss Alert Level: 0""",
]

# Regex patterns from specification
break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"

def validate_response(response_text):
    """Validate response format"""
    stress_match = re.search(stress_level_pattern, response_text)
    boss_match = re.search(boss_alert_pattern, response_text)
    summary_match = re.search(break_summary_pattern, response_text, re.MULTILINE)

    if not stress_match or not boss_match or not summary_match:
        return False, "Missing required fields"

    stress_val = int(stress_match.group(1))
    boss_val = int(boss_match.group(1))

    if not (0 <= stress_val <= 100):
        return False, f"Stress Level out of range: {stress_val}"

    if not (0 <= boss_val <= 5):
        return False, f"Boss Alert Level out of range: {boss_val}"

    return True, {
        "summary": summary_match.group(1),
        "stress": stress_val,
        "boss": boss_val
    }

print("=" * 60)
print("Response Format Validation")
print("=" * 60)

all_valid = True
for i, response in enumerate(sample_responses, 1):
    print(f"\nTest {i}:")
    print("-" * 40)
    print(response)
    print("-" * 40)

    is_valid, result = validate_response(response)

    if is_valid:
        print(f"✓ VALID")
        print(f"  Summary: {result['summary']}")
        print(f"  Stress: {result['stress']}")
        print(f"  Boss: {result['boss']}")
    else:
        print(f"✗ INVALID: {result}")
        all_valid = False

print("\n" + "=" * 60)
if all_valid:
    print("✓ All sample responses are valid!")
    print("✓ Regex patterns work correctly!")
else:
    print("✗ Some responses failed validation")
print("=" * 60)
