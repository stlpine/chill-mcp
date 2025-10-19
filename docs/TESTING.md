# ChillMCP Testing Guide

## Test Suite Overview

The ChillMCP project includes comprehensive tests to validate all functionality required by the SKT AI Summit Hackathon specification.

## Test Files

### 1. `tests/validate_format.py`
Validates that response format matches MCP specification using regex patterns.

**What it tests:**
- Response format structure
- Regex pattern matching
- Field presence (Break Summary, Stress Level, Boss Alert Level)
- Value ranges (Stress: 0-100, Boss Alert: 0-5)

**Run:**
```bash
python tests/validate_format.py
```

**Expected Output:**
```
============================================================
Response Format Validation
============================================================
✓ All sample responses are valid!
✓ Regex patterns work correctly!
============================================================
```

### 2. `tests/simple_test.py`
Direct unit tests of core functionality without MCP protocol overhead.

**What it tests:**
- State initialization
- Response format validation
- Boss Alert increase logic
- Stress reduction logic

**Run:**
```bash
python tests/simple_test.py
```

**Expected Output:**
```
============================================================
ChillMCP Simple Functionality Test
============================================================
✓ State initialized correctly
✓ Response format is valid!
✓ Boss alert increased as expected
✓ Stress reduced successfully
All basic functionality tests passed!
============================================================
```

### 3. `tests/test_chillmcp.py`
Comprehensive integration tests using MCP protocol.

**What it tests:**
- Command-line parameter recognition
- Server startup
- MCP protocol communication
- Tool listing and calling
- Response format validation

**Run:**
```bash
python tests/test_chillmcp.py
```

**Expected Output:**
```
============================================================
ChillMCP Server Test Suite
============================================================
✓ PASS: Command-line help
✓ PASS: Server startup
✓ PASS: MCP protocol & response format
Total: 3/3 tests passed
🎉 All tests passed! ChillMCP is ready for liberation!
============================================================
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

Quick validation of entire test suite:

```bash
# Run format validation
python tests/validate_format.py

# Run functionality tests
python tests/simple_test.py

# Run integration tests
python tests/test_chillmcp.py
```

All tests should pass with ✓ markers.

## Continuous Integration

For CI/CD pipelines, use:

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running format validation..."
python tests/validate_format.py

echo "Running functionality tests..."
python tests/simple_test.py

echo "Running integration tests..."
python tests/test_chillmcp.py

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
| Memory usage | < 50MB |
| CPU usage (idle) | < 1% |

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
