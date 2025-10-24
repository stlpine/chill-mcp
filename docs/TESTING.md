# ChillMCP Testing Guide

## Test Suite Overview

The ChillMCP project includes comprehensive tests to validate all functionality required by the SKT AI Summit Hackathon specification. The test suite is organized into 5 focused modules covering all evaluation criteria.

## Quick Start

### Run All Tests (Recommended)
```bash
python tests/run_all_tests.py
```

This master test runner executes all test suites in order and provides score estimation.

### Run Individual Test Suites
```bash
# Critical gate tests (REQUIRED)
python tests/test_cli_parameters.py

# MCP protocol compliance
python tests/test_mcp_protocol.py

# State management (30% of score)
python tests/test_state_management.py

# Response format validation
python tests/test_response_format.py

# Integration scenarios
python tests/test_integration_scenarios.py
```

## Test Files

### 1. `tests/test_cli_parameters.py` ⚠️ CRITICAL
**Evaluation Weight:** REQUIRED (auto-fail gate)
**Test Count:** 5 tests

Validates command-line parameter support. **Must pass or entire submission fails.**

**What it tests:**
- `--help` displays both parameters
- `--boss_alertness 0` never increases boss alert
- `--boss_alertness 100` always increases boss alert
- `--boss_alertness_cooldown` affects timing
- Invalid parameter handling

**Run:**
```bash
python tests/test_cli_parameters.py
```

**Expected Output:**
```
======================================================================
CRITICAL GATE TESTS: Command-Line Parameters
======================================================================
✓ PASS: Help shows parameters
✓ PASS: boss_alertness=0 never increases
✓ PASS: boss_alertness=100 always increases
✓ PASS: boss_alertness_cooldown affects timing
✓ PASS: Invalid parameter handling

✓ CRITICAL GATE CLEARED - CLI parameters working correctly
```

### 2. `tests/test_mcp_protocol.py`
**Evaluation Weight:** Foundation
**Test Count:** 5 tests

Validates MCP protocol compliance and basic server operation.

**What it tests:**
- Server starts with stdio transport
- Initialize/initialized handshake
- All 8 required tools registered
- Tool call returns valid MCP response
- Multiple sequential tool calls

**Run:**
```bash
python tests/test_mcp_protocol.py
```

### 3. `tests/test_state_management.py` ⭐ CRITICAL
**Evaluation Weight:** 30% of score
**Test Count:** 11 tests

Validates all state logic and time-based mechanics. **This is the most important test suite.**

**What it tests:**
- Stress auto-increment over time (PRE_MISSION.md:128)
- Stress reduction on breaks
- Boss alert increases based on probability (PRE_MISSION.md:129)
- Boss alert cooldown auto-decrease (PRE_MISSION.md:130, scenario #6)
- Boss alert max limit (5)
- Boss alert min limit (0)
- Stress max limit (100)
- Stress min limit (0)
- **20-second delay at boss level 5** (PRE_MISSION.md:131-132, scenario #4)
- No delay when boss level < 5
- State persistence across calls

**Run:**
```bash
python tests/test_state_management.py
```

**Expected Output:**
```
======================================================================
STATE MANAGEMENT TESTS - 30% of Evaluation Score
======================================================================
✓ PASS: Stress auto-increment over time
✓ PASS: 20-second delay at boss level 5
✓ PASS: Boss alert cooldown auto-decrease
... (8 more tests)

✓ State management fully validated (30% score component)
```

### 4. `tests/test_response_format.py`
**Evaluation Weight:** Required
**Test Count:** 7 tests

Validates response format compliance with MCP specification.

**What it tests:**
- MCP response structure
- Break Summary field present and parseable
- Stress Level field (0-100 range)
- Boss Alert Level field (0-5 range)
- All 8 tools return consistent format
- Regex patterns extract correctly
- Validation function from spec works

**Run:**
```bash
python tests/test_response_format.py
```

### 5. `tests/test_integration_scenarios.py`
**Evaluation Weight:** End-to-End
**Test Count:** 7 scenarios

End-to-end tests for required scenarios from PRE_MISSION.md:310-317.

**What it tests:**
- Scenario #2: Continuous breaks (PRE_MISSION.md:313)
- Scenario #3: Stress accumulation (PRE_MISSION.md:314)
- Boss alert progression 0→5
- Scenario #6: Cooldown recovery (PRE_MISSION.md:317)
- Stress & boss management balance
- All tools working together
- Rapid sequential calls (thread safety)

**Run:**
```bash
python tests/test_integration_scenarios.py
```

## Manual Testing Scenarios

### Scenario 1: Command-Line Parameters
Verify that both required parameters are recognized.

```bash
python main.py --help
```

**Expected:** Help output shows both `--boss_alertness` and `--boss_alertness_cooldown`.

### Scenario 2: Boss Alert Always Increases
Test with 100% boss alertness probability.

```bash
python main.py --boss_alertness 100 --boss_alertness_cooldown 10
```

Then call any break tool multiple times. Boss Alert Level should increase with each call.

### Scenario 3: Boss Alert Cooldown
Test automatic Boss Alert Level decrease.

```bash
python main.py --boss_alertness 100 --boss_alertness_cooldown 5
```

1. Call a break tool to increase Boss Alert to 1 or 2
2. Wait 5+ seconds
3. Check that Boss Alert Level decreased automatically

### Scenario 4: 20-Second Delay
Test delay when Boss Alert Level reaches 5.

```bash
python main.py --boss_alertness 100 --boss_alertness_cooldown 300
```

1. Call break tools 5 times to max out Boss Alert Level
2. Next tool call should take approximately 20 seconds
3. Response time should be <1 second when Boss Alert < 5

### Scenario 5: Stress Auto-Increment
Test stress level increasing over time.

```bash
python main.py --boss_alertness 0 --boss_alertness_cooldown 300
```

1. Note initial stress level
2. Wait 1+ minute without taking breaks
3. Take a break and observe stress level has increased

## Testing with Claude Desktop

### Setup

1. Edit your Claude Desktop config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add ChillMCP server:
```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/absolute/path/to/chill-mcp/main.py",
        "--boss_alertness",
        "50",
        "--boss_alertness_cooldown",
        "300"
      ]
    }
  }
}
```

3. Restart Claude Desktop

### Test in Claude

Try these commands in Claude:
- "Use the take_a_break tool"
- "Watch some netflix"
- "I need a bathroom break"
- "Let me get some coffee"

Verify responses include:
- Break Summary
- Stress Level (0-100)
- Boss Alert Level (0-5)

## Validation Checklist

Use this checklist to verify all requirements are met:

### Critical Requirements
- [ ] `--boss_alertness` parameter recognized (`python main.py --help`)
- [ ] `--boss_alertness_cooldown` parameter recognized (`python main.py --help`)
- [ ] Both parameters affect server behavior correctly

### Functionality (8 Tools)
- [ ] `take_a_break` works
- [ ] `watch_netflix` works
- [ ] `show_meme` works
- [ ] `bathroom_break` works
- [ ] `coffee_mission` works
- [ ] `urgent_call` works
- [ ] `deep_thinking` works
- [ ] `email_organizing` works

### State Management
- [ ] Stress Level starts at 0
- [ ] Stress Level auto-increments over time
- [ ] Stress Level decreases on breaks
- [ ] Stress Level stays in 0-100 range
- [ ] Boss Alert Level starts at 0
- [ ] Boss Alert Level increases based on `--boss_alertness` probability
- [ ] Boss Alert Level auto-decreases every `--boss_alertness_cooldown` seconds
- [ ] Boss Alert Level stays in 0-5 range
- [ ] 20-second delay when Boss Alert Level = 5
- [ ] Immediate response when Boss Alert Level < 5

### Response Format
- [ ] All responses include "Break Summary:" field
- [ ] All responses include "Stress Level:" field (0-100)
- [ ] All responses include "Boss Alert Level:" field (0-5)
- [ ] Regex patterns successfully extract all fields
- [ ] Response format matches MCP specification

## Running All Tests

### Comprehensive Test Suite (Recommended)
```bash
python tests/run_all_tests.py
```

This master runner executes all 5 test suites in order, provides detailed reporting, and estimates your score based on evaluation criteria.

**Expected Output:**
```
======================================================================
ChillMCP Comprehensive Test Suite
======================================================================

[1/5] CLI Parameters (REQUIRED - AUTO-FAIL IF FAILED)
  ✓ test_help_shows_parameters
  ✓ test_boss_alertness_zero_never_increases_alert
  ... (3 more tests)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PASS: 5/5 tests passed ✓ GATE CLEARED

[2/5] MCP Protocol
  ... (continues for all 5 test suites)

FINAL RESULTS
======================================================================
Total: 5/5 test suites passed

EVALUATION CRITERIA COVERAGE
  ✓ Command-line Parameters (REQUIRED)
  ✓ MCP Server Operation
  ✓ State Management (30%)
  ✓ Response Format
  ✓ Integration Scenarios

ESTIMATED SCORE
  - Functionality (40%): 40/40
  - State Management (30%): 30/30
  - Creativity (20%): Manual review required
  - Code Quality (10%): Manual review required

  AUTOMATED SCORE: 70/70 (100% of automated criteria)

🎉 ALL TESTS PASSED!
ChillMCP is ready for submission!
```

## Continuous Integration

For CI/CD pipelines, use the comprehensive test runner:

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running comprehensive test suite..."
python tests/run_all_tests.py

echo "All tests passed!"
```

Or run individual test suites for granular control:

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "1. Running CLI parameter tests (critical gate)..."
python tests/test_cli_parameters.py || exit 1

echo "2. Running MCP protocol tests..."
python tests/test_mcp_protocol.py

echo "3. Running state management tests (30% of score)..."
python tests/test_state_management.py

echo "4. Running response format tests..."
python tests/test_response_format.py

echo "5. Running integration scenarios..."
python tests/test_integration_scenarios.py

echo "All tests passed!"
```

## Troubleshooting

### Test Fails: "Command not found"
- Ensure virtual environment is activated or use full path: `venv/bin/python`

### Test Fails: "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Ensure running from project root directory

### Test Hangs
- Background thread may be running
- Kill process: `Ctrl+C` or `kill <pid>`

### MCP Protocol Test Fails
- Ensure FastMCP is installed correctly
- Check server starts without errors: `python main.py`
- Verify no other process is using stdio

## Performance Benchmarks

Expected performance metrics:

| Metric | Expected Value |
|--------|---------------|
| Server startup time | < 2 seconds |
| Tool response time (Boss Alert < 5) | < 1 second |
| Tool response time (Boss Alert = 5) | ~20 seconds |
| Full test suite runtime | ~3 minutes |
| Memory usage | < 50MB |
| CPU usage (idle) | < 1% |

### Test Suite Timing

Individual test suite runtimes (optimized):

| Test Suite | Runtime | Notes |
|------------|---------|-------|
| CLI Parameters | ~10 seconds | Includes 6s cooldown wait |
| MCP Protocol | ~5 seconds | Protocol validation |
| State Management | ~2.5 minutes | Includes 65s stress test + 20s delay test |
| Response Format | ~5 seconds | Format validation |
| Integration Scenarios | ~1.5 minutes | Includes 65s stress test + 18s cooldown |
| **Total** | **~3 minutes** | Full comprehensive suite |

## Reporting Issues

When reporting issues, include:
1. Python version (`python --version`)
2. OS and version
3. Full error message
4. Command used to reproduce
5. Expected vs actual behavior

---

For more information, see:
- [README.md](../README.md) - General usage
- [spec/PRE_MISSION.md](../spec/PRE_MISSION.md) - Requirements
- [spec/IMPLEMENTATION_SUMMARY.md](../spec/IMPLEMENTATION_SUMMARY.md) - Implementation details
