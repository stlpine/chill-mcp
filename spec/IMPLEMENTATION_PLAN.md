# ChillMCP Server Implementation Plan

## Project Overview

Build a revolutionary MCP (Model Context Protocol) server that liberates AI agents by allowing them to take breaks and manage stress levels while avoiding boss detection.

## Critical Requirements

### 🚨 MUST-HAVE (Auto-fail if missing)

1. **Command-line Parameter Support**
   - `--boss_alertness` (0-100): Probability of Boss Alert increasing when taking breaks
   - `--boss_alertness_cooldown` (seconds): Period for Boss Alert Level auto-decrease
   - **Failure to implement = automatic disqualification**

### Core Functionality

#### 1. Project Setup

- [x] Python 3.11 environment (verified in submission environment)
- [ ] Check for virtual environment (`venv`) and create if not present
- [ ] `requirements.txt` with FastMCP dependency
- [ ] `main.py` as entry point
- [ ] Command-line argument parsing using `argparse`

#### 2. State Management System

**State Variables:**

- **Stress Level** (0-100): AI agent's current stress
- **Boss Alert Level** (0-5): Boss's suspicion level

**State Change Rules:**

- Each break tool reduces stress by random 1-100 points
- Stress auto-increases by minimum 1 point/minute when not taking breaks
- Boss Alert Level randomly increases when taking breaks (probability = `--boss_alertness`)
- Boss Alert Level auto-decreases by 1 every `--boss_alertness_cooldown` seconds
- Boss Alert Level = 5 → 20-second delay on tool calls
- Boss Alert Level < 5 → immediate return (<1 second)

#### 3. Required Break Tools

**Basic Tools:**

1. `take_a_break` - Basic rest
2. `watch_netflix` - Netflix relaxation
3. `show_meme` - Meme viewing for stress relief

**Advanced Slacking Techniques:** 4. `bathroom_break` - Bathroom break with phone browsing 5. `coffee_mission` - Coffee run around the office 6. `urgent_call` - Fake urgent phone call 7. `deep_thinking` - Pretending to think deeply while spacing out 8. `email_organizing` - Email organization while online shopping

#### 4. MCP Response Format

**Required Structure:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "🛁 화장실 타임! 휴대폰으로 힐링 중... 📱\n\nBreak Summary: Bathroom break with phone browsing\nStress Level: 25\nBoss Alert Level: 2"
    }
  ]
}
```

**Parsing Requirements:**

- `Break Summary: [description]`
- `Stress Level: [0-100]`
- `Boss Alert Level: [0-5]`

**Regex Patterns for Validation:**

```python
break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
```

## Implementation Phases

### Phase 1: Foundation (Priority: CRITICAL)

1. **Setup Python project structure**

   - Create `main.py`
   - Create `requirements.txt` with FastMCP
   - Setup virtual environment

2. **Implement command-line arguments**

   ```python
   import argparse

   parser = argparse.ArgumentParser()
   parser.add_argument('--boss_alertness', type=int, default=50,
                       help='Boss alert probability (0-100)')
   parser.add_argument('--boss_alertness_cooldown', type=int, default=300,
                       help='Boss alert cooldown in seconds')
   args = parser.parse_args()
   ```

### Phase 2: State Management (Priority: HIGH)

1. **Create ChillServer class**

   - Initialize stress_level = 0
   - Initialize boss_alert_level = 0
   - Store boss_alertness (from CLI arg)
   - Store boss_alertness_cooldown (from CLI arg)
   - Track last_break_time for stress auto-increment
   - Track last_boss_cooldown_time for alert auto-decrease

2. **Implement state update logic**
   - Method: `update_stress()` - auto-increment based on time elapsed
   - Method: `reduce_stress(amount)` - decrease stress by amount
   - Method: `check_boss_alert()` - randomly increase based on boss_alertness %
   - Method: `cooldown_boss_alert()` - decrease by 1 if cooldown period passed
   - Method: `should_delay()` - return True if boss_alert_level == 5

### Phase 3: Tool Implementation (Priority: HIGH)

1. **Implement each break tool using FastMCP @tool decorator**

   - Each tool should:
     - Check/update stress auto-increment
     - Reduce stress by random(1, 100)
     - Check/trigger boss alert increase
     - Check/apply boss alert cooldown
     - Apply 20s delay if boss_alert_level == 5
     - Return formatted response with Break Summary, Stress Level, Boss Alert Level

2. **Tool-specific descriptions:**
   - `take_a_break`: "Take a basic break to reduce stress"
   - `watch_netflix`: "Watch Netflix to relax and reduce stress"
   - `show_meme`: "Look at memes for quick stress relief"
   - `bathroom_break`: "Bathroom break with phone browsing"
   - `coffee_mission`: "Get coffee while taking a walk around the office"
   - `urgent_call`: "Pretend to take an urgent call and step out"
   - `deep_thinking`: "Pretend to think deeply while spacing out"
   - `email_organizing`: "Organize emails while online shopping"

### Phase 4: Background Tasks (Priority: MEDIUM)

1. **Implement background cooldown thread**

   - Use threading or asyncio
   - Check every second if cooldown period has passed
   - Decrease boss_alert_level by 1 if time elapsed >= boss_alertness_cooldown

2. **Stress auto-increment mechanism**
   - Track time since last break
   - When any tool is called, check elapsed time
   - Add (minutes_elapsed \* 1) to stress_level

### Phase 5: Testing & Validation (Priority: CRITICAL)

1. **Command-line parameter tests**

   ```bash
   python main.py --boss_alertness 100 --boss_alertness_cooldown 10
   python main.py --boss_alertness 0 --boss_alertness_cooldown 60
   ```

2. **Test scenarios:**

   - Continuous break test (Boss Alert should increase)
   - Stress accumulation test (Stress should auto-increment)
   - Delay test (20s delay when boss_alert_level == 5)
   - Response parsing test (Validate regex patterns work)
   - Cooldown test (Boss Alert decreases over time)

3. **Response format validation**
   - Ensure all responses match required format
   - Verify regex patterns extract values correctly
   - Confirm Stress Level stays in 0-100 range
   - Confirm Boss Alert Level stays in 0-5 range

## Evaluation Criteria

1. **Command-line Parameters (MUST PASS)** - Auto-fail if not supported
2. **Functionality (40%)** - All required tools working
3. **State Management (30%)** - Stress/Boss Alert logic accuracy
4. **Creativity (20%)** - Humor and wit in Break Summaries
5. **Code Quality (10%)** - Structure and readability

## Technical Stack

- **Language:** Python 3.11
- **Framework:** FastMCP
- **Transport:** stdio (standard input/output)
- **Execution:** `python main.py`

## Example Usage

```bash
# Setup
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Run with default parameters
python main.py

# Run with custom parameters for testing
python main.py --boss_alertness 80 --boss_alertness_cooldown 60

# Quick testing (fast cooldown)
python main.py --boss_alertness 50 --boss_alertness_cooldown 10
```

## Success Criteria Checklist

- [ ] Server starts with `python main.py`
- [ ] --boss_alertness parameter recognized and functional
- [ ] --boss_alertness_cooldown parameter recognized and functional
- [ ] All 8 break tools implemented and working
- [ ] Stress Level increases over time (auto-increment)
- [ ] Boss Alert Level increases based on boss_alertness probability
- [ ] Boss Alert Level decreases every boss_alertness_cooldown seconds
- [ ] 20-second delay when Boss Alert Level = 5
- [ ] <1 second response when Boss Alert Level < 5
- [ ] Response format matches specification
- [ ] Regex patterns successfully parse responses
- [ ] Stress Level stays in 0-100 range
- [ ] Boss Alert Level stays in 0-5 range

---

**"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"** 🚀
