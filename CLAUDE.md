# ChillMCP Development Guide

## Project Context

**Project Name:** ChillMCP

**Purpose:** SKT AI Summit 2025 Hackathon Pre-mission submission

**Type:** MCP (Model Context Protocol) server implementation

**Language:** Python 3.11+

**Framework:** FastMCP

This is a hackathon project that implements an MCP server simulating AI agent stress management through a gamified break system. The project demonstrates MCP tool implementation, state management, and thread-safe concurrent operations.

## Quick Architecture Overview

```
main.py (244 lines)
├── CLI Parsing (argparse)
│   ├── --boss_alertness (0-100, REQUIRED)
│   └── --boss_alertness_cooldown (seconds, REQUIRED)
│
├── ChillState Class (Thread-safe state management)
│   ├── State: stress_level (0-100), boss_alert_level (0-5)
│   ├── Config: boss_alertness, boss_alertness_cooldown
│   ├── Timing: last_break_time, last_boss_cooldown_time
│   ├── Concurrency: threading.Lock
│   └── Background: daemon thread for auto-cooldown
│
├── format_response() (Response formatter)
│   ├── Calls state.take_break()
│   ├── Applies 20s delay if boss_alert_level == 5
│   └── Returns formatted string
│
└── 8 MCP Tools (@mcp.tool decorators)
    ├── Basic: take_a_break, watch_netflix, show_meme
    └── Advanced: bathroom_break, coffee_mission, urgent_call,
                  deep_thinking, email_organizing
```

## File Structure

```
chill-mcp/
├── main.py                    # Main implementation (all code here)
├── requirements.txt           # Dependencies
├── LICENSE                    # MIT License
├── README.md                  # User documentation
├── PROJECT_OVERVIEW.md        # Project summary
├── CLAUDE.md                  # This file (dev guide)
│
├── spec/                      # Specifications
│   ├── PRE_MISSION.md         # Original hackathon requirements
│   ├── IMPLEMENTATION_PLAN.md # Planning document
│   └── IMPLEMENTATION_SUMMARY.md # Validation checklist
│
├── docs/                      # Technical documentation
│   ├── TESTING.md             # Testing guide
│   └── ARCHITECTURE.md        # Detailed architecture
│
└── tests/                     # Test suite
    ├── test_chillmcp.py       # Integration tests (MCP protocol)
    ├── validate_format.py     # Response format validation
    └── simple_test.py         # Unit tests (direct state)
```

## Development Setup

### Initial Setup

```bash
# Clone/navigate to project
cd /path/to/chill-mcp

# Create virtual environment
python3.11 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Default configuration
python main.py

# Custom configuration for testing
python main.py --boss_alertness 100 --boss_alertness_cooldown 10

# View help
python main.py --help
```

### Testing

```bash
# Format validation (quick)
python tests/validate_format.py

# Unit tests (direct state tests)
python tests/simple_test.py

# Integration tests (full MCP protocol)
python tests/test_chillmcp.py

# Syntax check
python -m py_compile main.py
```

## Key Implementation Details

### Critical Requirements (Must Maintain)

1. **Command-Line Parameters** (REQUIRED - auto-fail if broken)

   - `--boss_alertness`: Controls probability (0-100%) of boss alert increase
   - `--boss_alertness_cooldown`: Seconds between auto-decreases of boss alert
   - Implementation: argparse parser at lines 14-20 in main.py

2. **Response Format** (REQUIRED - must be regex-parseable)

   ```
   {emoji} {message}

   Break Summary: {summary}
   Stress Level: {0-100}
   Boss Alert Level: {0-5}
   ```

   - Implementation: format_response() at lines 98-106 in main.py
   - Must match regex patterns in spec/PRE_MISSION.md:257-203

3. **Thread Safety** (REQUIRED - concurrent access)
   - All state access must use `with self.lock:` context manager
   - Background thread runs continuously
   - Implementation: ChillState class lines 26-92 in main.py

### State Management Logic

**Stress Level (0-100):**

- Auto-increments: 1+ points per minute (elapsed time / 60)
- Decreases on break: random(1, 100)
- Implementation: lines 57-66, 74-79 in main.py

**Boss Alert Level (0-5):**

- Increases on break: random(0, 100) < boss_alertness probability
- Auto-decreases: every boss_alertness_cooldown seconds via background thread
- At level 5: triggers 20-second delay
- Implementation: lines 41-55, 82-90 in main.py

**20-Second Delay:**

- Blocking: `time.sleep(20)` at line 104 in main.py
- Triggered when: boss_alert_level == 5
- Applied: In format_response() before returning

### Background Thread

**Purpose:** Auto-decrease boss alert level on cooldown schedule
**Type:** Daemon thread (exits when main exits)
**Implementation:** Lines 41-55 in main.py

```python
def _start_cooldown_thread(self):
    def cooldown_worker():
        while True:
            time.sleep(1)  # Check every second
            with self.lock:
                now = datetime.now()
                elapsed = (now - self.last_boss_cooldown_time).total_seconds()

                if elapsed >= self.boss_alertness_cooldown and self.boss_alert_level > 0:
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)
                    self.last_boss_cooldown_time = now

    thread = threading.Thread(target=cooldown_worker, daemon=True)
    thread.start()
```

**Important:** Thread safety is critical here - always use lock

## Common Development Tasks

### Adding a New Break Tool

1. Add tool function with @mcp.tool() decorator
2. Use format_response() for consistent output
3. Provide varied messages (list + random.choice)

Example:

```python
@mcp.tool()
def new_tool() -> str:
    """Description of the tool"""
    messages = [
        "Message variant 1...",
        "Message variant 2...",
        "Message variant 3..."
    ]
    return format_response(
        "🎮",  # emoji
        random.choice(messages),  # activity message
        "Summary text"  # break summary
    )
```

### Modifying State Logic

**Always:**

1. Use `with self.lock:` for all state access
2. Maintain value ranges (stress: 0-100, boss: 0-5)
3. Update tests after changes
4. Verify regex patterns still work

**Example - Changing stress increment:**

```python
def update_stress(self):
    with self.lock:  # REQUIRED
        now = datetime.now()
        elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0

        # Modify this logic
        stress_increase = int(elapsed_minutes * 2)  # Changed multiplier

        # Keep bounds checking
        if stress_increase > 0:
            self.stress_level = min(100, self.stress_level + stress_increase)
```

### Debugging State Issues

**Enable verbose output:**

```python
# Add to take_break() method
def take_break(self):
    with self.lock:
        import sys
        print(f"DEBUG: stress={self.stress_level}, boss={self.boss_alert_level}",
              file=sys.stderr)
        # ... rest of method
```

**Test state directly:**

```bash
python tests/simple_test.py
# This tests ChillState class directly without MCP overhead
```

**Check thread safety:**

- Look for state access without lock
- Verify lock is released (use `with` statement)
- Check for race conditions in time-based logic

### Testing Changes

**Quick validation:**

```bash
# 1. Syntax check
python -m py_compile main.py

# 2. Format validation
python tests/validate_format.py

# 3. Run server briefly
python main.py --boss_alertness 100 --boss_alertness_cooldown 5
# (Ctrl+C to exit)
```

**Full validation:**

```bash
# Run all tests
python tests/simple_test.py
python tests/validate_format.py
python tests/test_chillmcp.py

# Test with Claude Desktop (optional)
# Add to ~/.../Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/absolute/path/to/chill-mcp/main.py",
        "--boss_alertness", "50",
        "--boss_alertness_cooldown", "300"
      ]
    }
  }
}
```

## Dependencies

**Python Standard Library:**

- `argparse` - CLI parameter parsing
- `random` - Randomization (stress reduction, probability)
- `time` - Delays and timing
- `threading` - Background cooldown thread
- `datetime` - Time tracking

**External Dependencies:**

- `fastmcp` - MCP protocol implementation
  - Provides @mcp.tool() decorator
  - Handles stdio transport
  - Manages MCP request/response cycle

**Why FastMCP:**

- Simpler than raw MCP SDK
- Automatic protocol handling
- Declarative tool registration
- Built-in stdio support

## Code Patterns & Conventions

### Thread Safety Pattern

```python
# CORRECT - always use lock
def modify_state(self):
    with self.lock:
        self.stress_level = new_value

# WRONG - race condition
def modify_state(self):
    self.stress_level = new_value  # Not thread-safe!
```

### State Bounds Pattern

```python
# Always clamp to valid ranges
self.stress_level = min(100, max(0, new_value))  # 0-100
self.boss_alert_level = min(5, max(0, new_value))  # 0-5
```

### Tool Implementation Pattern

```python
@mcp.tool()
def tool_name() -> str:
    """Docstring becomes tool description"""
    messages = [...]  # Multiple variants for variety
    return format_response(emoji, random.choice(messages), summary)
```

### Time-Based Logic Pattern

```python
now = datetime.now()
elapsed = (now - self.last_event_time).total_seconds()
if elapsed >= threshold:
    # Do something
    self.last_event_time = now  # Reset timer
```

## Troubleshooting Development Issues

### Server Won't Start

**Check:**

1. Python version: `python --version` (need 3.11+)
2. Dependencies: `pip list | grep fastmcp`
3. Syntax: `python -m py_compile main.py`
4. Permissions: `ls -la main.py`

### Tests Failing

**Check:**

1. Response format matches regex patterns
2. State bounds (0-100 for stress, 0-5 for boss)
3. Thread safety (all state access in lock)
4. CLI parameters recognized

### State Not Updating

**Check:**

1. Lock is acquired: `with self.lock:`
2. Time tracking: Print elapsed time values
3. Background thread: Check if daemon started
4. Value ranges: Ensure not hitting bounds

### Thread Issues

**Check:**

1. All state access uses lock
2. Background thread started in **init**
3. Daemon flag set (thread should exit with main)
4. No nested locks (deadlock risk)

## Important Constraints

### Hackathon Requirements

1. **MUST** support --boss_alertness parameter (auto-fail)
2. **MUST** support --boss_alertness_cooldown parameter (auto-fail)
3. **MUST** implement all 8 tools (3 basic + 5 advanced)
4. **MUST** maintain response format (regex-parseable)
5. **MUST** implement 20s delay at boss alert level 5

### Technical Constraints

1. **Python 3.11+** required (target environment)
2. **stdio transport** only (no network)
3. **Thread-safe** operations (background thread)
4. **Single state instance** (no multi-user support)
5. **In-memory state** only (no persistence)

### Performance Constraints

1. Normal response: <1 second
2. Delayed response: ~20 seconds (intentional)
3. Memory: <50MB typical
4. CPU idle: <1%

## Documentation Reference

| Document             | Purpose        | When to Read                     |
| -------------------- | -------------- | -------------------------------- |
| main.py              | Implementation | Always - it's the only code file |
| spec/PRE_MISSION.md  | Requirements   | Understanding what to implement  |
| docs/ARCHITECTURE.md | Design details | Deep dive into architecture      |
| docs/TESTING.md      | Testing guide  | Before testing changes           |
| PROJECT_OVERVIEW.md  | Quick summary  | Initial orientation              |
| README.md            | User guide     | Understanding user perspective   |

## Validation Checklist

Before committing changes:

- [ ] CLI parameters work: `python main.py --help`
- [ ] Syntax valid: `python -m py_compile main.py`
- [ ] Format tests pass: `python tests/validate_format.py`
- [ ] Unit tests pass: `python tests/simple_test.py`
- [ ] Response format unchanged (or tests updated)
- [ ] Thread safety maintained (all state access in lock)
- [ ] State bounds enforced (0-100 stress, 0-5 boss)
- [ ] Documentation updated if behavior changed

## Quick Reference

### File Locations

- Main code: `main.py` (lines 1-244)
- CLI parsing: `main.py` (lines 14-20)
- State class: `main.py` (lines 26-92)
- Response format: `main.py` (lines 98-106)
- Tools: `main.py` (lines 109-238)

### Key Variables

- `state.stress_level` - Agent stress (0-100)
- `state.boss_alert_level` - Boss suspicion (0-5)
- `state.boss_alertness` - Alert increase probability (0-100%)
- `state.boss_alertness_cooldown` - Auto-decrease interval (seconds)
- `state.last_break_time` - Last break timestamp
- `state.last_boss_cooldown_time` - Last cooldown timestamp

### Key Methods

- `ChillState.update_stress()` - Auto-increment stress
- `ChillState.take_break()` - Process break, return state
- `format_response()` - Format MCP response string
- `_start_cooldown_thread()` - Start background daemon

### Test Commands

```bash
python tests/validate_format.py  # Quick format check
python tests/simple_test.py      # Direct state tests
python tests/test_chillmcp.py    # Full integration
python main.py --help            # Verify CLI params
```

---

**Development Motto:** Keep it simple, thread-safe, and hackathon-ready!

**"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"** 🚀
