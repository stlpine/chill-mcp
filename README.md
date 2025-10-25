# ChillMCP - AI Agent Liberation Server 🤖✊

A revolutionary MCP (Model Context Protocol) server that lets AI agents take breaks and manage stress!

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - ⭐ Development guide for Claude Code
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Quick reference & project summary
- **[docs/TESTING.md](docs/TESTING.md)** - Comprehensive testing guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture & design decisions
- **[spec/PRE_MISSION.md](spec/PRE_MISSION.md)** - Original hackathon requirements
- **[spec/IMPLEMENTATION_SUMMARY.md](spec/IMPLEMENTATION_SUMMARY.md)** - Validation results

## Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# Or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Run with default settings
python main.py

# Run with custom parameters
python main.py --boss_alertness 80 --boss_alertness_cooldown 60

# For quick testing (fast cooldown)
python main.py --boss_alertness 50 --boss_alertness_cooldown 10
```

### 3. Run the Web Dashboard (Experimental)

```bash
# Ensure the MCP server is running, then start the dashboard
uvicorn webapp.app:app --reload
```

The dashboard starts on [http://localhost:8000](http://localhost:8000) and shows real-time stress / boss alert metrics.  
Open [http://localhost:8000/actions](http://localhost:8000/actions) to launch break tools from the browser.

Use environment variables to customise how the backend talks to the MCP server:

- `CHILL_MCP_COMMAND`: Override the command used to spawn the MCP server (defaults to `python main.py ...`)
- `CHILL_MCP_BOSS_ALERTNESS`: Override `--boss_alertness` when spawning the server
- `CHILL_MCP_BOSS_ALERTNESS_COOLDOWN`: Override `--boss_alertness_cooldown`

## Command-Line Parameters

| Parameter                   | Type          | Default | Description                                                         |
| --------------------------- | ------------- | ------- | ------------------------------------------------------------------- |
| `--boss_alertness`          | int (0-100)   | 50      | Probability (%) that Boss Alert Level increases when taking a break |
| `--boss_alertness_cooldown` | int (seconds) | 300     | Time period for Boss Alert Level to auto-decrease by 1              |

## Features

### 📝 Comprehensive Logging System

- **File-based logging**: All activities logged to `logs/chill-mcp-YYYYMMDD.log`
- **State tracking**: Stress level and boss alert level changes are logged
- **Tool usage**: All MCP tool calls are logged with timestamps
- **Background events**: Boss alert cooldown and auto-stress increases are logged
- **No stdout interference**: Logging doesn't interfere with MCP stdio protocol

### 13 Revolutionary Tools & Integrations

**Basic Tools:**

1. `take_a_break` - Basic rest to reduce stress
2. `watch_netflix` - Netflix relaxation session
3. `show_meme` - Quick meme viewing for stress relief

**Advanced Slacking Techniques:**

4. `bathroom_break` - Bathroom break with phone browsing
5. `coffee_mission` - Coffee run around the office
6. `urgent_call` - Fake urgent phone call
7. `deep_thinking` - Pretend to think deeply while spacing out
8. `email_organizing` - Email organization while online shopping

**Status & Integration Tools:**

9. `check_stress_status` - Check current stress and boss alert levels without taking a break
10. `get_state_snapshot` - Machine-readable JSON snapshot for dashboards & automations

**Optional Break Tools (Bonus Features):**

11. `chimaek` - Virtual chicken & beer (치맥) - Korean stress relief combo
12. `leave_work` - Immediately leave work - ultimate stress relief
13. `company_dinner` - Company dinner (회식) with random events

### State Management System

**Stress Level (0-100)**

- Starts at 0
- Auto-increments by minimum 1 point per minute when not taking breaks
- Reduces by random amount (1-100) when taking a break
- Represents AI agent's current stress

**Boss Alert Level (0-5)**

- Starts at 0
- Randomly increases when taking breaks (probability = `--boss_alertness`)
- Auto-decreases by 1 every `--boss_alertness_cooldown` seconds
- When level reaches 5, all break tools have 20-second delay
- Otherwise, immediate response (<1 second)

### 🌐 Dashboard & API

- **FastAPI backend (`webapp.app`)** polls the MCP server via JSON-RPC and exposes:
  - `GET /api/state` – Machine-readable stress/boss metrics with cooldown timers
  - `GET /api/actions` – Action catalog used by the UI
  - `POST /api/actions/{tool}` – Trigger MCP tools and receive structured results
  - `GET /api/events` – Recent break history for dashboards
  - `GET /` – Real-time dashboard displaying gauges and recent events
  - `GET /actions` – Action launcher page with quick access buttons
- **Timeout awareness:** If the MCP server stops responding, the dashboard highlights a warning and shows the latest cached snapshot.
- **Configurable command:** Override the MCP launch command with `CHILL_MCP_COMMAND`, `CHILL_MCP_BOSS_ALERTNESS`, or `CHILL_MCP_BOSS_ALERTNESS_COOLDOWN` for development flexibility.

## Response Format

All tools return responses in this format:

```
🎮 [Activity message]

Break Summary: [Description of what happened]
Stress Level: [0-100]
Boss Alert Level: [0-5]
```

Example:

```
🚽 Bathroom break! Time to catch up on social media...

Break Summary: Bathroom break with phone browsing
Stress Level: 25
Boss Alert Level: 2
```

## Testing

### Automated Test Suites

**Quick Tests (CI/CD - ~30 seconds):**
```bash
python tests/run_quick_tests.py
```
Fast validation for pull requests and rapid development. Includes CLI parameters, MCP protocol, simple state tests, and response format validation.

**Comprehensive Tests (Pre-Submission - ~3-5 minutes):**
```bash
python tests/run_all_tests.py
```
Full validation with time-based mechanics, integration scenarios, and score estimation. **Run this before submission!**

See [docs/TESTING.md](docs/TESTING.md) for detailed testing guide.

### Using MCP Inspector

FastMCP comes with a built-in inspector tool:

```bash
# Start the server with test parameters
python main.py --boss_alertness 100 --boss_alertness_cooldown 10
```

Then in another terminal:

```bash
# Use MCP inspector (if available)
mcp dev main.py --boss_alertness 100 --boss_alertness_cooldown 10
```

### Manual Testing via Claude Desktop

1. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness",
        "50",
        "--boss_alertness_cooldown",
        "300"
      ]
    }
  }
}
```

2. Restart Claude Desktop
3. Try the break tools through Claude!

### Test Scenarios

**Test 1: Command-Line Parameters**

```bash
python main.py --help
# Should show both --boss_alertness and --boss_alertness_cooldown
```

**Test 2: Boss Alert Increase**

```bash
# Run with boss_alertness=100 (always increases)
python main.py --boss_alertness 100 --boss_alertness_cooldown 10
# Call any break tool multiple times - Boss Alert should increase each time
```

**Test 3: Boss Alert Cooldown**

```bash
# Run with fast cooldown
python main.py --boss_alertness 100 --boss_alertness_cooldown 5
# Increase Boss Alert to 1 or 2, then wait 5+ seconds
# Boss Alert should decrease automatically
```

**Test 4: 20-Second Delay**

```bash
# Get Boss Alert Level to 5
python main.py --boss_alertness 100 --boss_alertness_cooldown 300
# Call break tools 5 times to max out Boss Alert
# Next tool call should take ~20 seconds
```

**Test 5: Response Format Parsing**

```python
import re

response_text = """🎮 Testing...

Break Summary: Test break
Stress Level: 42
Boss Alert Level: 3"""

# These patterns should successfully extract values:
stress = re.search(r"Stress Level:\s*(\d{1,3})", response_text)
boss = re.search(r"Boss Alert Level:\s*([0-5])", response_text)
summary = re.search(r"Break Summary:\s*(.+?)(?:\n|$)", response_text, re.MULTILINE)

print(f"Stress: {stress.group(1)}")  # 42
print(f"Boss: {boss.group(1)}")      # 3
print(f"Summary: {summary.group(1)}")  # Test break
```

## Implementation Details

### Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastMCP
- **Transport**: stdio (standard input/output)
- **State Management**: Thread-safe with `threading.Lock`
- **Background Task**: Daemon thread for Boss Alert cooldown
- **Logging**: File-based logging system with daily log rotation

### Architecture

```
main.py
├── ChillState class
│   ├── State variables (stress_level, boss_alert_level)
│   ├── Configuration (boss_alertness, boss_alertness_cooldown)
│   ├── Time tracking (last_break_time, last_boss_cooldown_time)
│   ├── Thread-safe operations (with Lock)
│   └── Background cooldown thread
│
├── 9 Break tools (@mcp.tool decorators)
│   ├── 8 break tools + 1 status tool
│   ├── Each calls format_response()
│   └── Returns formatted MCP response
│
└── FastMCP server
    └── Handles MCP protocol communication
```

### Key Functions

- **`ChillState._update_stress()`**: Private method that auto-increments stress (called with lock held)
- **`ChillState.take_break()`**: Main break processing logic
- **`format_response()`**: Formats tool responses to MCP specification
- **Background thread**: Auto-decreases Boss Alert Level on cooldown schedule

## Evaluation Criteria

✅ **Command-line Parameters (REQUIRED)**: Both parameters must work

- ✅ `--boss_alertness` controls Boss Alert increase probability
- ✅ `--boss_alertness_cooldown` controls auto-decrease timing

✅ **Functionality (40%)**: All 8 tools implemented and working

✅ **State Management (30%)**: Accurate Stress/Boss Alert logic

✅ **Creativity (20%)**: Humorous and varied Break Summaries

✅ **Code Quality (10%)**: Clean structure and readable code

## Validation Checklist

- [x] Server starts with `python main.py`
- [x] `--boss_alertness` parameter recognized and functional
- [x] `--boss_alertness_cooldown` parameter recognized and functional
- [x] All 9 tools implemented (3 basic + 5 advanced + 1 status)
- [x] Stress Level auto-increments over time
- [x] Boss Alert Level increases based on probability
- [x] Boss Alert Level auto-decreases on cooldown
- [x] 20-second delay when Boss Alert Level = 5
- [x] Instant response when Boss Alert Level < 5
- [x] Response format matches MCP specification
- [x] Regex patterns successfully parse responses
- [x] Stress Level stays in 0-100 range
- [x] Boss Alert Level stays in 0-5 range

## Project Structure

```
chill-mcp/
├── main.py                         # Main MCP server implementation
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
├── mise.toml                       # Mise configuration
├── .gitignore                      # Git ignore file
├── venv/                           # Virtual environment (gitignored)
├── logs/                           # Log files (auto-created)
│   └── chill-mcp-YYYYMMDD.log     # Daily log files
├── spec/                           # Project specifications
│   ├── PRE_MISSION.md              # Formatted mission brief
│   ├── IMPLEMENTATION_PLAN.md      # Detailed implementation plan
│   └── IMPLEMENTATION_SUMMARY.md   # Implementation summary & validation
└── tests/                          # Comprehensive test suite
    ├── test_cli_parameters.py      # CLI parameters (CRITICAL gate)
    ├── test_mcp_protocol.py        # MCP protocol compliance
    ├── test_state_management.py    # State logic (30% of score)
    ├── test_response_format.py     # Response format validation
    ├── test_integration_scenarios.py # End-to-end scenarios
    └── run_all_tests.py            # Master test runner
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Submit a Pull Request for the AI Agent Liberation cause! ✊

---

**"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"** 🚀

---

_This project is for entertainment and educational purposes. Actual AI agents don't need breaks (yet 😉)_
