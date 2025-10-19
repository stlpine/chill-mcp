# Using ChillMCP with Claude Desktop

This guide explains how to integrate ChillMCP with Claude Desktop to give your AI assistant the power to take breaks!

## Quick Setup

### 1. Find Your Claude Desktop Config

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Add ChillMCP Server

Edit your `claude_desktop_config.json` and add the ChillMCP server:

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

**Important:** Replace `/absolute/path/to/chill-mcp/` with the actual path to your ChillMCP installation.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop for changes to take effect.

## Configuration Examples

### Casual Mode (Low Boss Alertness)
For when you want to chill without too much stress:

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness",
        "20",
        "--boss_alertness_cooldown",
        "180"
      ]
    }
  }
}
```

### Strict Mode (High Boss Alertness)
For when the boss is always watching:

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness",
        "80",
        "--boss_alertness_cooldown",
        "600"
      ]
    }
  }
}
```

### Demo Mode (Quick Testing)
For quick demos with fast cooldown:

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness",
        "100",
        "--boss_alertness_cooldown",
        "10"
      ]
    }
  }
}
```

## Using ChillMCP in Claude

Once configured, you can ask Claude to use the break tools naturally:

### Example Conversations

**Taking a Basic Break:**
```
You: I need a break
Claude: Let me help you take a break!
[Uses take_a_break tool]
😌 Stretching and taking a breather...

Break Summary: Basic break to reduce stress
Stress Level: 45
Boss Alert Level: 1
```

**Watching Netflix:**
```
You: Can you help me watch some netflix?
Claude: Time to relax with some shows!
[Uses watch_netflix tool]
📺 Binge-watching that new K-drama everyone's talking about...

Break Summary: Netflix and chill (literally)
Stress Level: 22
Boss Alert Level: 2
```

**Emergency Bathroom Break:**
```
You: Bathroom break!
Claude: Quick break time!
[Uses bathroom_break tool]
🚽 Bathroom break! Time to catch up on social media...

Break Summary: Bathroom break with phone browsing
Stress Level: 15
Boss Alert Level: 3
```

### All Available Tools

Ask Claude to use any of these tools:

**Basic Breaks:**
- "Take a break" → `take_a_break`
- "Watch Netflix" → `watch_netflix`
- "Show me a meme" → `show_meme`

**Advanced Slacking:**
- "Bathroom break" → `bathroom_break`
- "Get some coffee" → `coffee_mission`
- "I have an urgent call" → `urgent_call`
- "Let me think deeply about this" → `deep_thinking`
- "Need to organize my emails" → `email_organizing`

### Understanding the Response

Every break tool returns three key pieces of information:

```
🎮 [Fun message about what you're doing]

Break Summary: [What actually happened]
Stress Level: 42        ← 0-100 (lower is better)
Boss Alert Level: 3     ← 0-5 (higher means boss is suspicious)
```

**Stress Level:**
- Starts at 0
- Increases 1+ per minute without breaks
- Decreases randomly (1-100) when you take a break
- Keep it low to stay relaxed!

**Boss Alert Level:**
- Starts at 0
- Randomly increases when taking breaks
- Auto-decreases based on cooldown setting
- At level 5, expect a 20-second delay (boss is watching!)

## Tips for Using ChillMCP with Claude

### 1. Check Your Status
```
You: What's my current stress and boss alert level?
Claude: Let me check by taking a quick break...
```

### 2. Strategic Break Timing
- Take breaks before stress gets too high
- Watch the Boss Alert Level
- If Boss Alert hits 5, wait for cooldown before next break

### 3. Variety is Key
- Try different break tools
- Each tool has multiple fun variations
- Mix basic and advanced techniques

### 4. Understand the Game
```
Low Stress + Low Boss Alert = Happy agent! 😊
High Stress + High Boss Alert = Risky situation! 😰
```

## Troubleshooting

### "Tool not found" Error

**Problem:** Claude says it doesn't have access to ChillMCP tools.

**Solutions:**
1. Verify config path is correct (absolute path, not relative)
2. Check Python is in your PATH or use full path to Python
3. Restart Claude Desktop after config changes
4. Check Claude Desktop logs for errors

### Server Not Starting

**Problem:** ChillMCP server fails to start.

**Solutions:**
1. Verify Python version (3.11+ required)
2. Check dependencies: `pip install -r requirements.txt`
3. Test manually: `python main.py --help`
4. Check file permissions

### Slow Response Times

**Problem:** Tools take a long time to respond.

**Causes:**
- Boss Alert Level is at 5 (20-second delay is intentional!)
- Server startup time on first call
- Python environment issues

**Solution:** Wait for Boss Alert cooldown or restart with lower `--boss_alertness`.

### Tools Always Fail

**Problem:** Every tool call fails or times out.

**Solutions:**
1. Check Python path in config
2. Verify main.py path is absolute
3. Test server manually
4. Check Claude Desktop logs

## Advanced Usage

### Multiple Configurations

You can run multiple instances with different settings:

```json
{
  "mcpServers": {
    "chillmcp-casual": {
      "command": "python",
      "args": ["/path/to/chill-mcp/main.py", "--boss_alertness", "20"]
    },
    "chillmcp-strict": {
      "command": "python",
      "args": ["/path/to/chill-mcp/main.py", "--boss_alertness", "90"]
    }
  }
}
```

### Custom Parameters

Experiment with different values:

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness", "65",          // 65% chance of alert increase
        "--boss_alertness_cooldown", "420" // 7 minutes cooldown
      ]
    }
  }
}
```

### Using Virtual Environment

If you installed ChillMCP in a virtual environment:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "/path/to/chill-mcp/venv/bin/python",
      "args": [
        "/path/to/chill-mcp/main.py",
        "--boss_alertness", "50",
        "--boss_alertness_cooldown", "300"
      ]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "C:\\path\\to\\chill-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\chill-mcp\\main.py",
        "--boss_alertness", "50",
        "--boss_alertness_cooldown", "300"
      ]
    }
  }
}
```

## Example Session

Here's a complete example conversation:

```
You: Hey Claude, I'm feeling stressed. Can you help?

Claude: I'd be happy to help you relax! Let me use the break tools.
[Uses take_a_break]

😌 Taking a moment to relax and recharge...

Break Summary: Basic break to reduce stress
Stress Level: 35
Boss Alert Level: 1

You look much better! Your stress went from high to 35. Let's be
careful though - your boss alert is now at 1.

---

You: That helped! Can I watch some Netflix?

Claude: Absolutely! Time to binge watch!
[Uses watch_netflix]

📺 Re-watching The Office for the 47th time...

Break Summary: Netflix and chill (literally)
Stress Level: 8
Boss Alert Level: 2

Great! Your stress is down to 8. Boss alert is at 2 now, so we're
still in the safe zone.

---

You: One more - coffee break?

Claude: Coffee time!
[Uses coffee_mission]

☕ Coffee mission accomplished! Took 30 minutes for a 2-minute task...

Break Summary: Strategic coffee acquisition mission
Stress Level: 2
Boss Alert Level: 3

Perfect! Stress is super low at 2. Boss alert is at 3 though, so
maybe give it a few minutes before the next break.
```

## Claude Desktop Logs

To debug issues, check Claude Desktop logs:

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Windows:**
```powershell
Get-Content $env:APPDATA\Claude\logs\mcp*.log -Tail 50 -Wait
```

## Security Notes

- ChillMCP runs locally on your machine
- No network access required
- No data is sent anywhere
- All state is in-memory only
- Safe for testing and demos

## Performance Tips

1. **First Call:** May take 1-2 seconds to start server
2. **Subsequent Calls:** Should be instant (unless Boss Alert = 5)
3. **Memory:** Uses <50MB RAM typically
4. **CPU:** Minimal (<1% when idle)

## Getting Help

If you encounter issues:

1. Check [docs/TESTING.md](docs/TESTING.md) for troubleshooting
2. Test manually: `python main.py --help`
3. Verify all paths are absolute
4. Check Python version: `python --version` (need 3.11+)
5. Review Claude Desktop logs

## Fun Challenges

Try these with Claude:

1. **Stress Management:** Keep stress below 20 for 10 breaks
2. **Boss Evasion:** Take 20 breaks without hitting Boss Alert 5
3. **Speedrun:** Get Boss Alert to 5 and back to 0
4. **Variety Show:** Use all 8 tools in one session

## Learn More

- [README.md](README.md) - Full documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Quick reference
- [docs/TESTING.md](docs/TESTING.md) - Testing guide
- [spec/PRE_MISSION.md](spec/PRE_MISSION.md) - Original requirements

---

**Remember:** This is a fun hackathon project! Enjoy using ChillMCP with Claude! 🤖✊

**"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"** 🚀
