# ChillMCP Architecture

## System Overview

ChillMCP is an MCP (Model Context Protocol) server that simulates AI agent stress management through a gamified break system. The architecture is designed for simplicity, thread-safety, and compliance with MCP specifications.

## High-Level Architecture

```
┌───────────────────────────────────────────┐
│             MCP Client (Claude)            │
└──────────────────┬────────────────────────┘
                   │ JSON-RPC over stdio
┌──────────────────▼────────────────────────┐
│             FastMCP Runtime               │
│  ┌─────────────────────────────────────┐ │
│  │ application/controller.py          │ │
│  │  ├─ boots FastMCP                   │ │
│  │  └─ registers tools/responses       │ │
│  └──────────────────┬──────────────────┘ │
└─────────────────────┼────────────────────┘
                      │
┌─────────────────────▼────────────────────┐
│         presentation/tools.py            │
│  ├─ Builds (message, summary) options    │
│  └─ Uses state.perform_break + format_response│
└─────────────────────┬────────────────────┘
                      │
┌─────────────────────▼────────────────────┐
│        presentation/responses.py         │
│  └─ Pure formatter (no side effects)     │
└─────────────────────┬────────────────────┘
                      │
┌─────────────────────▼────────────────────┐
│            domain/state.py               │
│  ├─ AgentStressState (stress logic)      │
│  ├─ BossAlertState (probability/cooldown)│
│  └─ ChillState (lock + background thread)│
└──────────────────────────────────────────┘
```

## Component Details

### 1. Command-Line Argument Parsing

**Module:** `infrastructure/cli.py`

**Purpose:** Parse and validate command-line parameters required by the specification.

**Implementation:**
```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server",
    )
    parser.add_argument("--boss_alertness", type=int, default=50)
    parser.add_argument("--boss_alertness_cooldown", type=int, default=300)
    return parser

def parse_runtime_config(argv=None) -> RuntimeConfig:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not (0 <= args.boss_alertness <= 100):
        parser.error("boss_alertness must be between 0 and 100")
    if args.boss_alertness_cooldown < 0:
        parser.error("boss_alertness_cooldown must be non-negative")
    return RuntimeConfig(...)
```

**Design Decision:** Encapsulate parsing logic so tests and the CLI entry point share the same validations.

### 2. State Management (`domain/state.py`)

**Purpose:** Coordinate agent stress and boss alert levels with strict thread-safety guarantees.

**Components:**
- `AgentStressState` — handles elapsed-time stress increases and random reductions.
- `BossAlertState` — encapsulates probability-driven alert increases and cooldown timing.
- `ChillState` — orchestrates both models, manages the lock, and spawns the cooldown thread.

#### `AgentStressState.apply_elapsed_time()`
```python
def apply_elapsed_time(self) -> None:
    now = datetime.now()
    elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0
    increase = int(elapsed_minutes)
    if increase > 0:
        old_level = self.level
        self.level = min(100, self.level + increase)
        if self.level != old_level:
            self._logger.info("Stress auto-increased: %s -> %s", old_level, self.level)
```
- Calculates minutes since the last break and clamps stress level.
- Logging occurs only when the level changes to reduce noise.

#### `AgentStressState.reduce_for_break()`
```python
def reduce_for_break(self) -> int:
    reduction = random.randint(1, 100)
    old_level = self.level
    self.level = max(0, self.level - reduction)
    self.last_break_time = datetime.now()
    self._logger.info("Break taken - Stress: %s -> %s (-%s)", old_level, self.level, reduction)
    return reduction
```
- Applies random stress reduction, ensuring bounds and logging the change.

#### `ChillState.take_break()`
```python
def take_break(self) -> Tuple[int, int, bool]:
    with self.lock:
        self.agent.apply_elapsed_time()
        self.agent.reduce_for_break()
        boss_result = self.boss.register_break()
        if boss_result:
            old_level, new_level = boss_result
            self.logger.warning("Boss alert increased: %s -> %s", old_level, new_level)
        should_delay = self.boss.level == 5
        if should_delay:
            self.logger.warning("Boss alert level 5 reached! 20-second delay will be applied")
        return self.agent.level, self.boss.level, should_delay
```
- Ensures lock coverage across all state interactions.
- Delegates specific responsibilities to the stress/boss classes.
- Raises the delay flag when boss alert maxes out.

#### `ChillState.perform_break()`
```python
def perform_break(
    self,
    options: Sequence[Tuple[str, str]],
    apply_delay: bool = True,
) -> BreakOutcome:
    if not options:
        raise ValueError("Break options must not be empty")

    message, summary = random.choice(options)
    stress, boss, should_delay = self.take_break()

    delay_applied = False
    if should_delay and apply_delay:
        delay_applied = True
        self.logger.warning("Applying 20-second delay due to boss alert level 5")
        time.sleep(20)
        self.logger.info("20-second delay completed")

    return BreakOutcome(
        message=message,
        summary=summary,
        stress_level=stress,
        boss_alert_level=boss,
        delay_applied=delay_applied,
    )
```
- Handles meme/message selection within the domain layer.
- Applies the mandated 20-second delay when boss alert reaches level 5.
- Returns a `BreakOutcome` value object for presentation formatting.

### 3. Background Cooldown Thread

**Purpose:** Automatically decrease boss alert level over time without blocking.

**Implementation:**
```python
def _cooldown_worker(self) -> None:
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

**Design Decisions:**
- **Daemon thread:** Automatically exits when main program exits
- **1-second check interval:** Balance between responsiveness and CPU usage
- **Thread-safe:** Uses same lock as other state operations
- **No busy-waiting:** Uses `time.sleep(1)` to avoid CPU waste

### 4. Tool Implementation

**Framework:** FastMCP

**Pattern:** Each tool follows the same structure:
```python
@mcp.tool()
def tool_name() -> str:
    """Tool description"""
    options = [(message, summary) for message in messages for summary in summaries]
    outcome = state.perform_break(options)
    return format_response(
        emoji,
        outcome.message,
        outcome.summary,
        outcome.stress_level,
        outcome.boss_alert_level,
    )
```

**Design Decision:** Keep tools simple while delegating delay/meme selection to the domain layer.

### 5. Response Formatting

**Function:** `format_response(emoji, message, break_summary, stress, boss)`

**Implementation:**
```python
def format_response(
    emoji: str,
    message: str,
    break_summary: str,
    stress: int,
    boss: int,
) -> str:
    return (
        f"{emoji} {message}\n\n"
        f"Break Summary: {break_summary}\n"
        f"Stress Level: {stress}\n"
        f"Boss Alert Level: {boss}"
    )
```

**Design Decisions:**
- **Pure function:** No side effects; easy to unit test
- **String formatting:** Simple f-string for clarity and performance
- **Structured output:** Exact format required by regex validation patterns

## Thread Safety

### Why Thread Safety Matters

1. **Background cooldown thread** runs concurrently with tool calls
2. **Multiple MCP clients** could potentially call tools simultaneously
3. **State consistency** must be maintained across all operations

### Thread Safety Implementation

**Lock Usage:**
```python
class ChillState:
    def __init__(self):
        self.lock = threading.Lock()
        # ...

    def take_break(self):
        with self.lock:  # Acquire lock
            # All state modifications here
            pass
        # Lock automatically released
```

**Critical Sections Protected:**
- Reading/writing `stress_level`
- Reading/writing `boss_alert_level`
- Reading/writing time tracking variables
- All state calculations

### Deadlock Prevention

**Problem:** Python's `threading.Lock()` is non-reentrant - a thread cannot acquire the same lock twice.

**Solution:** Private methods called with lock already held
```python
def apply_elapsed_time(self):
    # NO lock acquisition - called by ChillState while lock already held
    now = datetime.now()
    # ... state updates ...

def take_break(self):
    with self.lock:  # Acquire lock once
        self.agent.apply_elapsed_time()  # Safe - lock already held
        # ... other state updates ...
```

**Key Points:**
- Private methods (prefix `_`) indicate they require lock held by caller
- No nested lock acquisition prevents deadlock
- All state access still protected by single lock

### Performance Considerations

- **Lock contention:** Minimal because tool calls are typically sequential
- **Lock duration:** Very short (milliseconds) for all operations
- **No deadlocks:** Single lock, no nested locking, private methods for lock-held calls

## Data Flow

### Tool Call Flow

```
1. User → MCP Client → FastMCP → @mcp.tool decorator
                                         ↓
2. format_response() called
                 ↓
3. state.take_break() called
                 ↓
4. Lock acquired
                 ↓
5. agent.apply_elapsed_time() - Calculate time-based stress increase
                 ↓
6. agent.reduce_for_break() - Reduce stress by random amount
                 ↓
7. Check boss_alertness probability → Possibly increase boss_alert_level
                 ↓
8. Update last_break_time
                 ↓
9. Check if delay needed (boss_alert_level == 5)
                 ↓
10. Lock released
                 ↓
11. Apply 20s delay if needed (outside lock)
                 ↓
12. Format and return response string
                 ↓
13. FastMCP wraps in MCP response format
                 ↓
14. JSON-RPC response → MCP Client → User
```

### Background Cooldown Flow

```
1. Daemon thread starts on ChillState initialization
                 ↓
2. Loop: sleep(1 second)
                 ↓
3. Lock acquired
                 ↓
4. Check elapsed time since last cooldown
                 ↓
5. If >= boss_alertness_cooldown seconds:
   - Decrease boss_alert_level by 1 (if > 0)
   - Update last_boss_cooldown_time
                 ↓
6. Lock released
                 ↓
7. Repeat from step 2
```

## Design Decisions & Tradeoffs

### 1. Single Global State Instance

**Decision:** Create one `ChillState` instance shared by all tools.

**Rationale:**
- Specification requires persistent state across tool calls
- Simpler than dependency injection
- No database or external storage needed

**Tradeoff:** Not suitable for multiple concurrent users (acceptable for MCP stdio transport).

### 2. Background Thread vs. Check-on-Call

**Decision:** Use background daemon thread for cooldown.

**Alternatives Considered:**
- Check cooldown on each tool call: Would miss cooldowns during idle periods
- Separate cooldown tool: User would need to manually trigger

**Rationale:** Background thread provides accurate, automatic cooldown regardless of activity.

### 3. Blocking 20-Second Delay

**Decision:** Use `time.sleep(20)` when boss_alert_level == 5.

**Alternatives Considered:**
- Return immediately with message: Wouldn't simulate real delay
- Async/non-blocking: MCP stdio transport is synchronous anyway

**Rationale:** Specification explicitly requires 20-second delay. Blocking is acceptable and accurate.

### 4. Random Stress Reduction

**Decision:** `random.randint(1, 100)` for stress reduction amount.

**Rationale:**
- Specification allows 1-100 range
- Adds gameplay variability
- Prevents predictable patterns

### 5. FastMCP Framework

**Decision:** Use FastMCP instead of raw MCP SDK.

**Rationale:**
- Simpler decorator-based API
- Automatic MCP protocol handling
- Built-in stdio transport
- Easier to implement and maintain

**Tradeoff:** Additional dependency, but specification allows it.

## Error Handling

### Current Implementation

**Philosophy:** Fail fast and explicit.

**Areas Covered:**
- Invalid argument types caught by argparse
- State value clamping (stress: 0-100, boss alert: 0-5)
- Thread exceptions isolated to background thread

### Areas Not Covered

**Intentionally omitted (acceptable for hackathon):**
- Network errors (stdio transport is local)
- Filesystem errors (no file operations)
- Memory exhaustion (state is minimal)
- Invalid MCP requests (handled by FastMCP)

## Performance Characteristics

### Memory Usage

- **State size:** ~200 bytes
- **Background thread:** ~8KB stack
- **Python runtime:** ~20-30MB
- **FastMCP overhead:** ~10-20MB
- **Total:** < 50MB typical

### CPU Usage

- **Idle:** < 1% (background thread sleeps)
- **Tool call:** < 5% for <100ms
- **20s delay:** 0% (sleeping)

### Latency

- **Normal tool call:** 10-50ms
- **Boss Alert Level 5:** 20 seconds + 10-50ms
- **Cooldown check:** < 1ms

## Testing Architecture

Tests are organized into 5 comprehensive suites mapped to evaluation criteria:

1. **CLI Parameters** (`test_cli_parameters.py`)
   - CRITICAL gate - auto-fail if failed
   - Tests `--boss_alertness` and `--boss_alertness_cooldown`

2. **MCP Protocol** (`test_mcp_protocol.py`)
   - MCP protocol compliance
   - Server startup and tool registration

3. **State Management** (`test_state_management.py`)
   - 30% of evaluation score
   - Stress/boss alert logic, cooldown, 20s delay

4. **Response Format** (`test_response_format.py`)
   - Response structure validation
   - Regex pattern extraction

5. **Integration Scenarios** (`test_integration_scenarios.py`)
   - End-to-end scenarios from PRE_MISSION.md
   - Thread safety and performance

**Master Runner:** `run_all_tests.py` executes all suites with score estimation

## Future Improvements

Potential enhancements (outside specification):

1. **Persistence:** Save state to disk for resume across restarts
2. **Multi-user:** Separate state per client ID
3. **Metrics:** Track usage statistics, average stress levels
4. **Configuration:** YAML/JSON config file
5. **Logging:** Structured logging for debugging
6. **Async:** AsyncIO for better concurrency (if MCP adds async support)
7. **Web UI:** Dashboard showing current state
8. **AI Integration:** LLM-generated break messages

## Compliance with Specification

| Requirement | Implementation | Verification |
|------------|----------------|--------------|
| --boss_alertness param | `infrastructure/cli.py` (argparse) | `python main.py --help` |
| --boss_alertness_cooldown param | `infrastructure/cli.py` (argparse) | `python main.py --help` |
| 12 break tools | `presentation/tools.py` (@mcp.tool) | Tool list in tests |
| Stress 0-100 | `AgentStressState` clamping | State tests |
| Boss Alert 0-5 | `BossAlertState` clamping | State tests |
| Stress auto-increment | `AgentStressState.apply_elapsed_time()` | Time-based tests |
| Boss Alert probability | `BossAlertState.register_break()` | Probability tests |
| Boss Alert cooldown | `ChillState._cooldown_worker()` | Cooldown tests |
| 20s delay at level 5 | `ChillState.perform_break()` | Integration tests |
| MCP response format | `presentation/responses.format_response()` | Regex validation |
| Thread safety | `ChillState.lock` usage | Concurrent tests |

## Conclusion

The ChillMCP architecture prioritizes:
1. **Simplicity:** Easy to understand and maintain
2. **Correctness:** Meets all specification requirements
3. **Thread Safety:** Reliable concurrent operations
4. **Performance:** Responsive and lightweight
5. **Testability:** Comprehensive test coverage

The design successfully balances hackathon time constraints with production-quality code patterns.
