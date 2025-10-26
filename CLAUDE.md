# ChillMCP Development Guide

## Project Context

**Project Name:** ChillMCP

**Purpose:** SKT AI Summit 2025 Hackathon Pre-mission submission

**Type:** MCP (Model Context Protocol) server implementation

**Language:** Python 3.11+

**Framework:** FastMCP

This is a hackathon project that implements an MCP server simulating AI agent stress management through a gamified break system. The project demonstrates MCP tool implementation, state management, and thread-safe concurrent operations.

> **⚠️ IMPORTANT:** When making any changes to this project, always update relevant documentation files to maintain consistency. See the [Documentation Maintenance](#documentation-maintenance) section for detailed guidelines.

## Quick Architecture Overview

```
main.py (33 lines) - Entry point and dependency wiring
├── infrastructure/
│   ├── cli.py (45 lines)              # argparse runtime config parsing
│   └── logging_config.py (28 lines)   # file-based logging bootstrap
├── domain/state.py (238 lines)        # Thread-safe state + break orchestration
│   ├── AgentStressState              # Stress auto-increment + break reduction
│   ├── BossAlertState                # Boss probability + cooldown management
│   └── ChillState                    # Service coordinating agent/boss + thread/delay
├── presentation/
│   ├── controller.py (37 lines)      # FastMCP wiring + lifecycle management
│   ├── tools.py (123 lines)          # Tool registration & option assembly
│   ├── responses.py (16 lines)       # Pure response formatting
│   └── message_catalog.py (271 lines)# Meme/message pools & summaries
└── tests/                            # Comprehensive automated suites
    ├── CLI, protocol, state, format tests (critical gates)
    └── run_quick_tests.py / run_all_tests.py (orchestrators)

12 MCP Tools registered (@mcp.tool):
  • 기본: take_a_break, watch_netflix, show_meme
  • 고급: bathroom_break, coffee_mission, urgent_call, deep_thinking, email_organizing
  • 기타: check_stress_status, chimaek, leave_work, company_dinner
```

## File Structure

```
chill-mcp/
├── main.py                  # Entry point (imports, controller bootstrap)
├── infrastructure/          # Runtime wiring
│   ├── cli.py               # argparse runtime configuration
│   └── logging_config.py    # Structured file logging setup
├── domain/                  # Core business logic
│   ├── models.py            # RuntimeConfig dataclass
│   └── state.py             # AgentStressState, BossAlertState, ChillState
├── presentation/            # MCP-facing layer
│   ├── controller.py        # FastMCP setup + lifecycle management
│   ├── tools.py             # Tool registration helpers
│   ├── responses.py         # Response formatting utilities
│   └── message_catalog.py   # Meme/message/summaries catalog
├── docs/                    # Technical documentation
│   ├── ARCHITECTURE.md
│   └── TESTING.md
├── spec/                    # Hackathon requirements & plans
├── tests/                   # Critical gates & integration tests
├── webapp/                  # (Optional) Dashboard implementation
├── requirements.txt
├── README.md
├── PROJECT_OVERVIEW.md
└── CLAUDE.md                # This development guide
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
# Quick tests (CI/CD - ~30 seconds)
python tests/run_quick_tests.py

# Comprehensive tests (Pre-submission - ~3-5 minutes)
python tests/run_all_tests.py

# Or run individual test suites
python tests/test_cli_parameters.py          # Critical gate
python tests/test_mcp_protocol.py            # MCP protocol
python tests/test_state_management.py        # State logic (30% of score)
python tests/simple_state_test.py            # Quick state tests
python tests/test_response_format.py         # Format validation
python tests/test_integration_scenarios.py   # End-to-end scenarios

# Syntax check
python -m py_compile main.py
```

## Key Implementation Details

### Critical Requirements (Must Maintain)

1. **Command-Line Parameters** (REQUIRED - auto-fail if broken)

   - `--boss_alertness`: Controls probability (0-100%) of boss alert increase
   - `--boss_alertness_cooldown`: Seconds between auto-decreases of boss alert
   - Implementation: `infrastructure/cli.py:9-45`

2. **Response Format** (REQUIRED - must be regex-parseable)

   ```
   {emoji} {message}

   Break Summary: {summary}
   Stress Level: {0-100}
   Boss Alert Level: {0-5}
   ```

   - Implementation: `presentation/responses.py` (pure formatter)
   - Must match regex patterns in spec/PRE_MISSION.md:257-203

3. **Thread Safety** (REQUIRED - concurrent access)
   - All state access must use `with self.lock:` context manager
   - Background thread runs continuously
   - Internal helpers (`AgentStressState.apply_elapsed_time`, `BossAlertState.register_break`) run inside the lock
   - Implementation: `domain/state.py` (ChillState + helpers)

### State Management Logic

**Stress Level (0-100):**

- Auto-increments: 1+ points per minute (elapsed time / 60)
- Decreases on break: random(1, 100)
 - Implementation: `AgentStressState.apply_elapsed_time()` / `AgentStressState.reduce_for_break()` (`domain/state.py`)

**Boss Alert Level (0-5):**

- Increases on break: random(0, 100) < boss_alertness probability
- Auto-decreases: every boss_alertness_cooldown seconds via background thread
- At level 5: triggers 20-second delay
 - Implementation: `BossAlertState.register_break()` / `BossAlertState.cooldown_step()` (`domain/state.py`)

**20-Second Delay:**

- Blocking: `time.sleep(20)` within `ChillState.perform_break()` (`domain/state.py`)
- Triggered when: boss_alert_level == 5
- Applied: In `ChillState.perform_break()` after state evaluation

### Background Thread

**Purpose:** Auto-decrease boss alert level on cooldown schedule
**Type:** Daemon thread (exits when main exits)
**Implementation:** `domain/state.py` (cooldown worker)

```python
def _cooldown_worker(self):
    while True:
        time.sleep(1)
        with self.lock:
            result = self.boss.cooldown_step(datetime.now())
            if result:
                old_level, new_level, elapsed = result
                self.logger.info(
                    "Boss alert cooldown: %s -> %s (elapsed: %.1fs)",
                    old_level,
                    new_level,
                    elapsed,
                )
```

**Important:** Thread safety is critical here - always use lock

## Common Development Tasks

### Adding a New Break Tool

1. Add tool function with @mcp.tool() decorator
2. Build `(message, summary)` option pairs (use helper if needed)
3. Call `controller.state.perform_break(options)` to mutate state + enforce delay
4. Pass outcome to `format_response()` for consistent formatting
5. **Update documentation** (see Documentation Maintenance section)

Example:

```python
@mcp.tool()
def new_tool() -> str:
    """Description of the tool"""
    options = [
        ("Message variant 1...", "Summary A"),
        ("Message variant 2...", "Summary B"),
        ("Message variant 3...", "Summary C"),
    ]
    outcome = controller.state.perform_break(options)
    return format_response(
        "🎮",
        outcome.message,
        outcome.summary,
        outcome.stress_level,
        outcome.boss_alert_level,
    )
```

**Documentation to update:**

- README.md: Add to features list
- CLAUDE.md: Update tool count in Quick Architecture Overview
- PROJECT_OVERVIEW.md: Add to Features Checklist
- Update line counts if main.py size changed significantly

### Modifying State Logic

**Always:**

1. Use `with self.lock:` for all state access
2. Maintain value ranges (stress: 0-100, boss: 0-5)
3. Update tests after changes
4. Verify regex patterns still work
5. **Update documentation** to reflect logic changes (see Documentation Maintenance section)

**Example - Changing stress increment:**

```python
def apply_elapsed_time(self):
    now = datetime.now()
    elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0

    # Modify this logic as needed
    stress_increase = int(elapsed_minutes * 2)  # Changed multiplier

    if stress_increase > 0:
        new_level = min(100, self.level + stress_increase)
        if new_level != self.level:
            self._logger.info(
                "Stress auto-increased: %s -> %s (+%s, elapsed: %.1fmin)",
                self.level,
                new_level,
                stress_increase,
                elapsed_minutes,
            )
            self.level = new_level
```

### Debugging State Issues

**Enable verbose output:**

```python
# Add near the top of ChillState.take_break()
with self.lock:
    import sys
    print(
        f"DEBUG: stress={self.agent.level}, boss={self.boss.level}",
        file=sys.stderr,
    )
    # ... rest of method
```

**Test state directly:**

```bash
python tests/test_state_management.py
# This tests all state logic including time-based mechanics (30% of score)
```

**Check thread safety:**

- Look for state access without lock
- Verify lock is released (use `with` statement)
- Check for race conditions in time-based logic

### Testing Changes

**Quick validation (CI/CD - ~30 seconds):**

```bash
# 1. Syntax check
python -m py_compile main.py

# 2. Run quick test suite
python tests/run_quick_tests.py

# 3. Run server briefly (optional)
python main.py --boss_alertness 100 --boss_alertness_cooldown 5
# (Ctrl+C to exit)
```

**Full validation (Pre-submission - ~3-5 minutes):**

```bash
# Run comprehensive tests (recommended before submission)
python tests/run_all_tests.py

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

## Documentation Maintenance

**IMPORTANT:** Whenever you modify the project, update all relevant documentation to maintain consistency.

### When to Update Documentation

**Always update documentation when:**

1. Adding/removing/modifying tools
2. Changing state management logic
3. Modifying response format
4. Changing CLI parameters
5. Updating line numbers or file structure
6. Adding new features or files
7. Changing dependencies

### Which Documents to Update

| Change Type            | Documents to Check/Update                                  |
| ---------------------- | ---------------------------------------------------------- |
| **Code changes**       | CLAUDE.md (line numbers), docs/ARCHITECTURE.md             |
| **New tools**          | README.md (features list), PROJECT_OVERVIEW.md (checklist) |
| **State logic**        | README.md (state management), docs/ARCHITECTURE.md         |
| **CLI parameters**     | README.md, CLAUDE.md, docs/ARCHITECTURE.md                 |
| **Response format**    | README.md (examples), docs/ARCHITECTURE.md                 |
| **File structure**     | CLAUDE.md (file structure), PROJECT_OVERVIEW.md            |
| **Testing changes**    | docs/TESTING.md, README.md (testing section)               |
| **Dependencies**       | README.md, CLAUDE.md (dependencies section)                |
| **Line count changes** | CLAUDE.md, PROJECT_OVERVIEW.md                             |

### Documentation Update Workflow

```bash
# 1. Make your code changes

# 2. Check line counts for touched modules
wc -l main.py domain/state.py presentation/tools.py

# 3. Update documentation with new counts and structural notes
# Update CLAUDE.md - Quick Architecture Overview (line counts)
# Update CLAUDE.md - File Locations (line ranges)
# Update PROJECT_OVERVIEW.md - Project Structure (line counts)
# Update PROJECT_OVERVIEW.md - Key Files table (line counts)

# 4. Update feature-specific documentation
# If tools changed: Update README.md features list
# If state logic changed: Update README.md state management section
# If architecture changed: Update docs/ARCHITECTURE.md

# 5. Verify consistency across all docs
# Search for old line numbers: grep -r "219 lines" .
# Search for outdated descriptions: Review all documentation files
```

### Common Documentation Inconsistencies to Avoid

1. **Line counts** - Update everywhere when core modules change

   - CLAUDE.md: Quick Architecture Overview + File Locations
   - PROJECT_OVERVIEW.md: Project Structure + Key Files table
   - docs/ARCHITECTURE.md: Diagrams or callouts referencing line ranges

2. **Tool lists** - Keep synchronized across files

   - README.md: Features section with all 8 tools
   - CLAUDE.md: Quick Architecture Overview tool list
   - PROJECT_OVERVIEW.md: Features Checklist

3. **File descriptions** - Use consistent terminology

   - CLAUDE.md should be described as "Development guide for Claude Code"
   - Not "Claude Desktop integration guide" or other variants

4. **Technical details** - Keep implementation details in sync
   - Response format examples
   - State management logic descriptions
   - CLI parameter descriptions
   - Performance metrics

### Quick Documentation Check

Before committing, verify consistency:

```bash
# Check for line count references to main.py/domain/state.py
grep -n "main.py.*lines" CLAUDE.md PROJECT_OVERVIEW.md
grep -n "domain/state.py" CLAUDE.md PROJECT_OVERVIEW.md

# Check for tool counts
grep -n "8 tools" README.md CLAUDE.md PROJECT_OVERVIEW.md

# Check for CLAUDE.md descriptions
grep -n "CLAUDE.md" README.md PROJECT_OVERVIEW.md

# Verify all docs mention both CLI parameters
grep -n "boss_alertness" README.md CLAUDE.md PROJECT_OVERVIEW.md docs/ARCHITECTURE.md
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

**Logging System:**

- `logging` - Python standard library logging
- File-based logging to avoid stdout interference
- Daily log rotation with date-based filenames
- Comprehensive state change tracking

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
    options = [...]  # Sequence of (message, summary) tuples
    outcome = controller.state.perform_break(options)
    return format_response(
        emoji,
        outcome.message,
        outcome.summary,
        outcome.stress_level,
        outcome.boss_alert_level,
    )
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
3. Full test suite: ~3 minutes (optimized)
4. Memory: <50MB typical
5. CPU idle: <1%

## Documentation Reference

| Document/Module                 | Purpose                                   | When to Read                     |
| ------------------------------- | ----------------------------------------- | -------------------------------- |
| main.py                         | Entry point + controller bootstrap        | Wiring overview before running   |
| infrastructure/cli.py           | CLI parsing & validation                  | Touching command-line behavior   |
| infrastructure/logging_config.py| Logging configuration details             | Adjusting log output             |
| domain/state.py                 | Core state & thread logic                 | Modifying stress/boss mechanics  |
| presentation/tools.py           | Tool registration + flow                  | Adding/updating MCP tools        |
| presentation/message_catalog.py | Message/meme content source               | Tweaking humor/summary content   |
| spec/PRE_MISSION.md             | Requirements                              | Understanding what to implement  |
| docs/ARCHITECTURE.md            | Design details                            | Deep dive into architecture      |
| docs/TESTING.md                 | Testing guide                             | Before testing changes           |
| PROJECT_OVERVIEW.md             | Quick summary                             | Initial orientation              |
| README.md                       | User guide                                | Understanding user perspective   |

## Validation Checklist

Before committing changes:

**Code Validation:**

- [ ] CLI parameters work: `python main.py --help`
- [ ] Syntax valid: `python -m py_compile main.py` and `python -m py_compile domain/state.py`
- [ ] All tests pass: `python tests/run_all_tests.py`
- [ ] CLI gate passes: `python tests/test_cli_parameters.py`
- [ ] State management passes (30%): `python tests/test_state_management.py`
- [ ] Thread safety maintained (all state access in lock)
- [ ] State bounds enforced (0-100 stress, 0-5 boss)

**Documentation Validation:**

- [ ] Line counts updated in CLAUDE.md and PROJECT_OVERVIEW.md
- [ ] Tool lists synchronized across README.md, CLAUDE.md, PROJECT_OVERVIEW.md
- [ ] File descriptions consistent across all documentation
- [ ] Technical details (state logic, response format) updated if changed
- [ ] Architecture documentation reflects current implementation
- [ ] Testing documentation updated if tests changed
- [ ] All affected documents reviewed and updated (see Documentation Maintenance section)

## Quick Reference

### File Locations

- Entry point: `main.py` (33 lines)
- CLI parsing: `infrastructure/cli.py` (45 lines)
- Logging bootstrap: `infrastructure/logging_config.py` (28 lines)
- Agent/boss state service: `domain/state.py` (238 lines)
- MCP controller: `presentation/controller.py` (37 lines)
- Tool registry: `presentation/tools.py` (123 lines)
- Response helpers: `presentation/responses.py` (16 lines)
- Message pools: `presentation/message_catalog.py` (271 lines)

### Key Variables

- `ChillState.agent.level` - Agent stress (0-100)
- `ChillState.agent.last_break_time` - Timestamp of last break
- `ChillState.boss.level` - Boss suspicion (0-5)
- `ChillState.boss.alertness_probability` - Alert increase chance (0-100%)
- `ChillState.boss.cooldown_seconds` - Auto-decrease interval (seconds)
- `ChillState.boss.last_cooldown_time` - Last cooldown timestamp

### Key Methods

- `AgentStressState.apply_elapsed_time()` - Auto-increment stress on access
- `AgentStressState.reduce_for_break()` - Random stress reduction
- `BossAlertState.register_break()` - Probabilistic boss increase
- `BossAlertState.cooldown_step()` - Background cooldown decrement
- `ChillState.take_break()` - Thread-safe orchestration (stress/boss calculation)
- `ChillState.perform_break()` - Applies delay when needed, returns outcome
- `presentation.responses.format_response()` - Pure string formatter

### Test Commands

```bash
python tests/run_quick_tests.py              # Quick tests (~30s, CI/CD)
python tests/run_all_tests.py                # Full tests (~3-5 min, pre-submission)
python tests/test_cli_parameters.py          # Critical gate
python tests/test_state_management.py        # State logic (30% of score) - Full
python tests/simple_state_test.py            # State logic - Quick
python tests/test_response_format.py         # Format validation
python main.py --help                        # Verify CLI params
```

---

**Development Motto:** Keep it simple, thread-safe, and hackathon-ready!

**"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"** 🚀
