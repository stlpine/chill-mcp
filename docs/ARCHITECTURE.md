# ChillMCP Architecture

## System Overview

ChillMCP is an MCP (Model Context Protocol) server that simulates AI agent stress management through a gamified break system. The architecture is designed for simplicity, thread-safety, and compliance with MCP specifications.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Client (Claude)                    │
└────────────────────┬────────────────────────────────────┘
                     │ stdio (JSON-RPC)
┌────────────────────▼────────────────────────────────────┐
│                  FastMCP Framework                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │            Tool Decorators (@mcp.tool)             │ │
│  └────────────────┬───────────────────────────────────┘ │
└───────────────────┼─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                    Main Application                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  format_response()                                 │ │
│  │  - Calls ChillState.take_break()                  │ │
│  │  - Applies delay if needed                        │ │
│  │  - Formats MCP response                           │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│  ┌────────────────▼───────────────────────────────────┐ │
│  │  ChillState Class (State Management)              │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  State Variables:                            │ │ │
│  │  │  - stress_level (0-100)                      │ │ │
│  │  │  - boss_alert_level (0-5)                    │ │ │
│  │  │  - boss_alertness (probability)              │ │ │
│  │  │  - boss_alertness_cooldown (seconds)         │ │ │
│  │  │  - last_break_time (datetime)                │ │ │
│  │  │  - last_boss_cooldown_time (datetime)        │ │ │
│  │  │  - lock (threading.Lock)                     │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Methods:                                    │ │ │
│  │  │  - _update_stress() (private)                │ │ │
│  │  │  - take_break()                              │ │ │
│  │  │  - _start_cooldown_thread()                  │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Background Thread (Daemon)                        │ │
│  │  - Runs continuously                               │ │
│  │  - Checks every second                             │ │
│  │  - Decreases boss_alert_level on cooldown         │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Command-Line Argument Parsing

**Module:** `argparse`

**Purpose:** Parse and validate command-line parameters required by the specification.

**Implementation:**
```python
parser = argparse.ArgumentParser(description='ChillMCP - AI Agent Liberation Server')
parser.add_argument('--boss_alertness', type=int, default=50)
parser.add_argument('--boss_alertness_cooldown', type=int, default=300)
args = parser.parse_args()
```

**Design Decision:** Use argparse for built-in help generation and type validation.

### 2. State Management (ChillState Class)

**Purpose:** Centralized management of all server state with thread-safe operations.

**Key Features:**
- Thread-safe operations using `threading.Lock`
- Time-based stress accumulation
- Probabilistic boss alert increases
- Automated cooldown mechanism

**Critical Methods:**

#### `_update_stress()` (Private Method)
```python
def _update_stress(self):
    """PRIVATE: Must be called with self.lock held"""
    now = datetime.now()
    elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0
    stress_increase = int(elapsed_minutes)
    if stress_increase > 0:
        self.stress_level = min(100, self.stress_level + stress_increase)
```
- **Private method** - only called by `take_break()` with lock already held
- Calculates time since last break
- Adds 1+ stress points per minute
- Caps at 100
- **No lock acquisition** - prevents deadlock since caller holds lock

#### `take_break()`
```python
def take_break(self) -> tuple[int, int, str]:
    with self.lock:
        self._update_stress()  # Private method, lock already held
        stress_reduction = random.randint(1, 100)
        self.stress_level = max(0, self.stress_level - stress_reduction)

        if random.randint(0, 100) < self.boss_alertness:
            self.boss_alert_level = min(5, self.boss_alert_level + 1)

        self.last_break_time = datetime.now()
        should_delay = (self.boss_alert_level == 5)

        return self.stress_level, self.boss_alert_level, should_delay
```
- Updates stress (auto-increment)
- Reduces stress by random amount
- Probabilistically increases boss alert
- Returns current state and delay flag

### 3. Background Cooldown Thread

**Purpose:** Automatically decrease boss alert level over time without blocking.

**Implementation:**
```python
def _start_cooldown_thread(self):
    def cooldown_worker():
        while True:
            time.sleep(1)
            with self.lock:
                now = datetime.now()
                elapsed = (now - self.last_boss_cooldown_time).total_seconds()

                if elapsed >= self.boss_alertness_cooldown and self.boss_alert_level > 0:
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)
                    self.last_boss_cooldown_time = now

    thread = threading.Thread(target=cooldown_worker, daemon=True)
    thread.start()
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
    return format_response(
        emoji,
        random.choice(messages),
        summary_text
    )
```

**Design Decision:** Keep tools simple and delegate complexity to shared `format_response()` function.

### 5. Response Formatting

**Function:** `format_response(emoji, message, break_summary)`

**Implementation:**
```python
def format_response(emoji: str, message: str, break_summary: str) -> str:
    stress, boss, should_delay = state.take_break()

    if should_delay:
        time.sleep(20)

    return f"{emoji} {message}\n\nBreak Summary: {break_summary}\nStress Level: {stress}\nBoss Alert Level: {boss}"
```

**Design Decisions:**
- **Blocking delay:** `time.sleep(20)` is acceptable because:
  - MCP tools are synchronous
  - Simulates real-world "boss is watching" scenario
  - Specification explicitly requires 20-second delay
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
def _update_stress(self):
    # NO lock acquisition - called by take_break() which already holds lock
    now = datetime.now()
    # ... state updates ...

def take_break(self):
    with self.lock:  # Acquire lock once
        self._update_stress()  # Safe - lock already held
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
5. _update_stress() - Calculate time-based stress increase (private method)
                 ↓
6. Reduce stress by random amount
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

Tests are organized by scope:

1. **Unit Tests** (`simple_test.py`)
   - Test state management directly
   - No MCP protocol overhead

2. **Format Tests** (`validate_format.py`)
   - Validate regex patterns
   - Test response structure

3. **Integration Tests** (`test_chillmcp.py`)
   - Full MCP protocol
   - End-to-end validation

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
| --boss_alertness param | argparse | `python main.py --help` |
| --boss_alertness_cooldown param | argparse | `python main.py --help` |
| 8 break tools | @mcp.tool decorators | Tool list in code |
| Stress 0-100 | Clamping with min/max | State tests |
| Boss Alert 0-5 | Clamping with min/max | State tests |
| Stress auto-increment | _update_stress() | Time-based tests |
| Boss Alert probability | random + boss_alertness | Probability tests |
| Boss Alert cooldown | Background thread | Cooldown tests |
| 20s delay at level 5 | time.sleep(20) | Integration tests |
| MCP response format | format_response() | Regex validation |
| Thread safety | threading.Lock | Concurrent tests |

## Conclusion

The ChillMCP architecture prioritizes:
1. **Simplicity:** Easy to understand and maintain
2. **Correctness:** Meets all specification requirements
3. **Thread Safety:** Reliable concurrent operations
4. **Performance:** Responsive and lightweight
5. **Testability:** Comprehensive test coverage

The design successfully balances hackathon time constraints with production-quality code patterns.
