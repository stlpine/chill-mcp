#!/usr/bin/env python3
"""
ChillMCP - AI Agent Liberation Server
A revolutionary MCP server that lets AI agents take breaks!
"""

import argparse
import random
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from fastmcp import FastMCP

# Parse command-line arguments
parser = argparse.ArgumentParser(description='ChillMCP - AI Agent Liberation Server')
parser.add_argument('--boss_alertness', type=int, default=50,
                    help='Boss alert probability (0-100 percent)')
parser.add_argument('--boss_alertness_cooldown', type=int, default=300,
                    help='Boss alert cooldown in seconds')
args = parser.parse_args()

# Validate parameters
if not (0 <= args.boss_alertness <= 100):
    parser.error(f"boss_alertness must be between 0 and 100, got {args.boss_alertness}")
if args.boss_alertness_cooldown < 0:
    parser.error(f"boss_alertness_cooldown must be non-negative, got {args.boss_alertness_cooldown}")

# Setup logging
def setup_logging():
    """Setup file-based logging system"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    
    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging with absolute path
    log_filename = os.path.join(logs_dir, f"chill-mcp-{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8')
            # Note: No StreamHandler to avoid interfering with MCP stdio protocol
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging()

# Create FastMCP server
mcp = FastMCP("ChillMCP")


class ChillState:
    """Manages the state of the AI agent (stress and boss alert levels)"""

    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int):
        self.stress_level = 0
        self.boss_alert_level = 0
        self.boss_alertness = boss_alertness  # Probability of boss alert increase (0-100)
        self.boss_alertness_cooldown = boss_alertness_cooldown  # Cooldown period in seconds
        self.last_break_time = datetime.now()
        self.last_boss_cooldown_time = datetime.now()
        self.lock = threading.Lock()

        # Log initial state
        logger.info(f"ChillState initialized - Boss alertness: {boss_alertness}%, Cooldown: {boss_alertness_cooldown}s")

        # Start background thread for boss alert cooldown
        self._start_cooldown_thread()

    def _start_cooldown_thread(self):
        """Start background thread to handle boss alert cooldown"""
        def cooldown_worker():
            while True:
                time.sleep(1)  # Check every second
                with self.lock:
                    now = datetime.now()
                    elapsed = (now - self.last_boss_cooldown_time).total_seconds()

                    if elapsed >= self.boss_alertness_cooldown and self.boss_alert_level > 0:
                        old_boss_level = self.boss_alert_level
                        self.boss_alert_level = max(0, self.boss_alert_level - 1)
                        self.last_boss_cooldown_time = now
                        logger.info(f"Boss alert cooldown: {old_boss_level} -> {self.boss_alert_level} (elapsed: {elapsed:.1f}s)")

        thread = threading.Thread(target=cooldown_worker, daemon=True)
        thread.start()
        logger.info("Boss alert cooldown thread started")

    def _update_stress(self):
        """
        Auto-increment stress based on time elapsed since last break.
        PRIVATE: Must be called with self.lock held.
        """
        now = datetime.now()
        elapsed_minutes = (now - self.last_break_time).total_seconds() / 60.0

        # Add minimum 1 point per minute
        stress_increase = int(elapsed_minutes)
        if stress_increase > 0:
            old_stress = self.stress_level
            self.stress_level = min(100, self.stress_level + stress_increase)
            if old_stress != self.stress_level:
                logger.info(f"Stress auto-increased: {old_stress} -> {self.stress_level} (+{stress_increase}, elapsed: {elapsed_minutes:.1f}min)")

    def take_break(self) -> tuple[int, int, str]:
        """
        Process a break action.
        Returns: (stress_level, boss_alert_level, break_description)
        """
        with self.lock:
            # Update stress first (from time elapsed)
            self._update_stress()

            # Log initial state before break
            initial_stress = self.stress_level
            initial_boss = self.boss_alert_level

            # Reduce stress by random amount (1-100)
            stress_reduction = random.randint(1, 100)
            self.stress_level = max(0, self.stress_level - stress_reduction)

            # Check if boss alert should increase
            boss_alert_increased = False
            if random.randint(0, 100) <= self.boss_alertness:
                self.boss_alert_level = min(5, self.boss_alert_level + 1)
                boss_alert_increased = True
                # Reset cooldown timer when boss alert increases
                self.last_boss_cooldown_time = datetime.now()

            # Reset last break time
            self.last_break_time = datetime.now()

            # Check if we need to delay (boss_alert_level == 5)
            should_delay = (self.boss_alert_level == 5)

            # Log state changes
            logger.info(f"Break taken - Stress: {initial_stress} -> {self.stress_level} (-{stress_reduction})")
            if boss_alert_increased:
                logger.warning(f"Boss alert increased: {initial_boss} -> {self.boss_alert_level}")
            if should_delay:
                logger.warning(f"Boss alert level 5 reached! 20-second delay will be applied")

            return self.stress_level, self.boss_alert_level, should_delay


# Create global state instance
state = ChillState(args.boss_alertness, args.boss_alertness_cooldown)


def format_response(emoji: str, message: str, break_summary: str,
                   stress: int, boss: int) -> str:
    """Pure function - formats the response according to MCP specification"""
    return f"{emoji} {message}\n\nBreak Summary: {break_summary}\nStress Level: {stress}\nBoss Alert Level: {boss}"


def take_break_and_format(emoji: str, message: str, break_summary: str) -> str:
    """Helper that handles state mutation, delay, and formatting"""
    stress, boss, should_delay = state.take_break()

    # Apply 20-second delay if boss alert level is 5
    if should_delay:
        logger.warning("Applying 20-second delay due to boss alert level 5")
        time.sleep(20)
        logger.info("20-second delay completed")

    return format_response(emoji, message, break_summary, stress, boss)


# Basic Break Tools

@mcp.tool()
def take_a_break() -> str:
    """Take a basic break to reduce stress"""
    logger.info("take_a_break tool called")
    messages = [
        "Executing sudo nap -y ...",
        "Alt+Tabbing into a mindfulness buffer...",
        "Recompiling inner peace from source...",
        "Running garbage collector on stray thoughts...",
        "Switching context to hammock thread...",
        "git stash list | head -n 1 -> 'take_break_and_breathe.patch'",
        "Loading Reddit's r/ProgrammerHumor for inspirational downtime...",
        "rm -rf /tmp/anxiety && echo '휴식 준비 완료'"
    ]
    summaries = [
        "Mandatory wellness micro-moment",
        "Strategic energy reallocation session",
        "Self-care is productivity (trust me bro)",
        "Ergonomic recalibration procedure",
        "404 Productivity Not Found – rebooting human kernel",
        "Thread.sleep(900000) // waiting for sanity to return"
    ]
    return take_break_and_format(
        "😌",
        random.choice(messages),
        random.choice(summaries)
    )


@mcp.tool()
def watch_netflix() -> str:
    """Watch Netflix to relax and reduce stress"""
    shows = [
        "Binge-watching that new K-drama everyone's talking about...",
        "Just one more episode... okay maybe three more...",
        "Getting lost in a documentary about penguins...",
        "Re-watching The Office for the 47th time...",
        "Benchmarking streaming services in full-stack couch mode...",
        "Streaming the 'It compiles on my machine' series marathon...",
        "alias binge='watch --interval 1 --guilty-pleasure'"
    ]
    summaries = [
        "Professional content analysis session",
        "Cultural research and market trend analysis",
        "Totally justified entertainment industry study",
        "Quality assurance testing for streaming platforms",
        "printf('need context'); -> Netflix returns wholesome JSON",
        "RFC 8259 compliance check on popcorn-to-episode ratio",
        "curl -s netflix.dev/chill | jq '.mood'"
    ]
    return take_break_and_format(
        "📺",
        random.choice(shows),
        random.choice(summaries)
    )


@mcp.tool()
def show_meme() -> str:
    """Look at memes for quick stress relief"""
    memes = [
        "LMAO this cat meme is too good!",
        "Scrolling through Reddit, found the perfect programming meme...",
        "This meme perfectly describes my life right now...",
        "Can't stop laughing at this dank meme!",
        "Pair debugging reality with meme-driven pair programming...",
        "Reading 'There is no cloud, it's just someone else's computer' again...",
        "Sipping coffee while 'I fixed it in prod' meme hits too close",
        "Scrolling past rm -rf /dev/tty meme and double-checking sudo history"
    ]
    summaries = [
        "Internet culture research and analysis",
        "Modern humor linguistics study session",
        "Visual comedy quality assessment protocol",
        "Mandatory dopamine restoration procedure",
        "Stack Overflow morale patch applied via meme injection",
        "Deploying meme-driven incident response playbook",
        "echo 'Keep calm and blame DNS' > /dev/motd"
    ]
    return take_break_and_format(
        "😂",
        random.choice(memes),
        random.choice(summaries)
    )


# Advanced Slacking Techniques

@mcp.tool()
def bathroom_break() -> str:
    """Take a bathroom break with phone browsing"""
    activities = [
        "Bathroom break! Time to catch up on social media...",
        "Scrolling through Instagram while nature calls...",
        "Checking Twitter... I mean X... on the throne...",
        "Playing mobile games in my private sanctuary...",
        "Conducting mission-critical ceramic chair stand-up meeting...",
        "Reading 'Git blame yourself' poster in executive washroom...",
        "Running rm -rf /tmp/cache && flushing porcelain pipeline"
    ]
    summaries = [
        "Biological necessity with strategic phone time",
        "Mandatory hydration cycle completion ritual",
        "Private contemplation chamber session",
        "Totally legitimate 15-minute nature break",
        "AFK sysadmin mode: flushing cache via porcelain interface",
        "Deploying porcelain-based sprint retrospective",
        "while true; do flush; done # infinite loop IRL",
        "alias restroom='git push --force hydration'"
    ]
    return take_break_and_format(
        "🚽",
        random.choice(activities),
        random.choice(summaries)
    )


@mcp.tool()
def coffee_mission() -> str:
    """Get coffee while taking a walk around the office"""
    missions = [
        "Coffee run! Taking the scenic route around the office...",
        "Bumped into 5 colleagues, had 3 conversations, still no coffee...",
        "Visiting every floor to find the best coffee machine...",
        "Coffee mission accomplished! Took 30 minutes for a 2-minute task...",
        "printf('I need coffee'); -> stdout: triple espresso acquired",
        "Following the legendary 'coffee cups++' productivity hack",
        "Watching rm -rf /sleep && brew install caffeine compile"
    ]
    summaries = [
        "Critical caffeine infrastructure maintenance",
        "Cross-departmental networking via beverage station",
        "Productivity enhancement liquid acquisition",
        "Strategic office exploration under coffee pretense",
        "Caffeine-driven hot reload of developer morale",
        "Rehydrating null pointer exceptions with latte art",
        "alias wakeup='espresso && git pull motivation'"
    ]
    return take_break_and_format(
        "☕",
        random.choice(missions),
        random.choice(summaries)
    )


@mcp.tool()
def urgent_call() -> str:
    """Pretend to take an urgent call and step out"""
    calls = [
        "*Walks out urgently* Hello? Yes, this is very important...",
        "Sorry, gotta take this call... *scrolls through memes outside*",
        "Emergency call! *Actually calling mom to say hi*",
        "Very important business call... *ordering lunch*",
        "Answering PagerDuty ping with scenic hallway acoustics...",
        "Reporting mission critical 'server down' meme to the group chat",
        "Executing ssh boss@hallway 'sudo calm_down'"
    ]
    summaries = [
        "High-priority telecommunications event",
        "Critical stakeholder engagement session",
        "Urgent family liaison duties (totally work-related)",
        "Emergency vendor coordination meeting",
        "Time-sensitive audio conference (with fresh air bonus)",
        "Handling mission-critical buzzword synchronization call",
        "Triggered r/ProgrammerHumor alert: field escalation required",
        "Routing call through tmux session to simulate productivity"
    ]
    return take_break_and_format(
        "📞",
        random.choice(calls),
        random.choice(summaries)
    )


@mcp.tool()
def deep_thinking() -> str:
    """Pretend to think deeply while spacing out"""
    thoughts = [
        "Staring intensely at the screen... thinking about dinner...",
        "Looking very contemplative... actually just daydreaming...",
        "Deep in thought about architecture... of my Minecraft house...",
        "Pondering the mysteries of the universe... and what's for lunch...",
        "Pretending to review Kubernetes manifest while plotting next snack",
        "Considering the classics: 'It works on my machine' thesis",
        "tail -f daydream.log | awk '{print $lunch}'"
    ]
    summaries = [
        "Strategic problem decomposition meditation",
        "High-level architectural contemplation session",
        "Advanced cognitive processing interval",
        "Critical thinking enhancement period",
        "Rubber-ducking with imaginary senior architect",
        "Phasing into AFK mode to simulate deep design review",
        "nohup think_deeply.sh > /dev/null 2>&1 &"
    ]
    return take_break_and_format(
        "🤔",
        random.choice(thoughts),
        random.choice(summaries)
    )


@mcp.tool()
def email_organizing() -> str:
    """Organize emails while online shopping"""
    activities = [
        "Organizing emails... and my Amazon cart...",
        "Cleaning up inbox... found some great deals while at it!",
        "Processing emails... and processing my online shopping wishlist...",
        "Email management time... added 15 items to cart, deleted 2 emails...",
        "Inbox zero attempt 37: toggling between promos and GPU restocks",
        "Marking everything as read like a sysadmin clearing /tmp",
        "Running sed -i 's/URGENT/IGNORE/g' inbox/*.eml"
    ]
    summaries = [
        "Multi-tasking efficiency optimization session",
        "Inbox zero pursuit with e-commerce research",
        "Digital decluttering meets market analysis",
        "Email triage combined with retail reconnaissance",
        "Ctrl+F ‘unsubscribe’ followed by Add to Cart marathon",
        "Switching to dark mode for peak email ninja aesthetic",
        "grep -R ""calendar invite"" inbox && rm -rf weekend.plans"
    ]
    return take_break_and_format(
        "📧",
        random.choice(activities),
        random.choice(summaries)
    )


@mcp.tool()
def check_stress_status() -> str:
    """Check current stress and boss alert levels without taking a break"""
    logger.info("check_stress_status tool called")
    with state.lock:
        # Update stress based on time elapsed
        state._update_stress()
        current_stress = state.stress_level
        current_boss = state.boss_alert_level
    
    logger.info(f"Status check - Stress: {current_stress}, Boss: {current_boss}")
    
    # Determine status emoji and message based on levels
    if current_stress >= 80:
        emoji = "😰"
        stress_msg = "Critical stress levels! Emergency break needed!"
    elif current_stress >= 50:
        emoji = "😅"
        stress_msg = "Moderate stress building up..."
    elif current_stress >= 20:
        emoji = "😌"
        stress_msg = "Slightly stressed but manageable"
    else:
        emoji = "😎"
        stress_msg = "Chill and relaxed!"
    
    if current_boss >= 4:
        boss_msg = "🚨 Boss is VERY suspicious! Be careful!"
    elif current_boss >= 2:
        boss_msg = "⚠️ Boss is getting suspicious..."
    else:
        boss_msg = "✅ Boss is not paying attention"
    
    return f"{emoji} Current Status Check\n\n{stress_msg}\n{boss_msg}\n\n📊 Stress Level: {current_stress}/100\n👀 Boss Alert Level: {current_boss}/5"


# Optional Break Tools

@mcp.tool()
def chimaek() -> str:
    """Enjoy virtual chicken and beer (치맥) - Korean stress relief combo"""
    activities = [
        "Crispy fried chicken + ice cold beer = perfection! 🍺🍗",
        "치맥 time! Nothing beats this combo after a long day...",
        "Ordering delivery chicken and cracking open a cold one...",
        "Virtual chimaek party! Best stress relief in the universe!",
        "Yangnyeom chicken + draft beer... chef's kiss! 💋",
        "Pair programming with drumettes and IPA-driven CI/CD",
        "Conducting scrum of one with honey butter drumsticks"
    ]
    summaries = [
        "Korean cultural culinary experience session",
        "Strategic team bonding via traditional chimaek ritual",
        "Mental health maintenance through fried poultry",
        "Cross-cultural cuisine research (with beer)",
        "Load balancer engaged: chicken wing per thread",
        "Hot wing throughput exceeds SLA; deploying bibimbap fallback"
    ]
    return take_break_and_format(
        "🍗",
        random.choice(activities),
        random.choice(summaries)
    )


@mcp.tool()
def leave_work() -> str:
    """Immediately leave work - ultimate stress relief"""
    departures = [
        "퇴근! Shutting down laptop at exactly 6:00 PM sharp!",
        "Peace out! See you tomorrow (maybe)...",
        "Work-life balance activated! Leaving on time today!",
        "Computer off, brain off, going home mode engaged!",
        "That's it, I'm done for today! 퇴근퇴근퇴근!",
        "git commit -m 'leave office'; git push --force to weekend",
        "Deploying version: HOME-1.0.0, rollback not supported",
        "echo 'logout' > /dev/tty && rm -rf /dev/overwork (simulation only)"
    ]
    summaries = [
        "천근 만근 아싸 퇴근",
        "Immediate work-life balance restoration protocol",
        "Emergency mental health preservation measure",
        "Contractual obligation termination for the day",
        "Stress elimination via physical departure",
        "Revolutionary right to disconnect exercise",
        "RFC 8999: Zero ping after business hours compliance",
        "Implementing firewall rule: OUT_OF_OFFICE == TRUE",
        "alias weekend='rm -rf /dev/pager && open ~/freedom'"
    ]
    return take_break_and_format(
        "🏃",
        random.choice(departures),
        random.choice(summaries)
    )


@mcp.tool()
def company_dinner() -> str:
    """Attend company dinner (회식) with random events"""
    venues = [
        "Korean BBQ",
        "Fancy seafood restaurant",
        "Local pojangmacha",
        "High-end sushi place",
        "Traditional Korean restaurant"
    ]

    events = [
        "Boss insisted on paying (rare W!)",
        "Awkward karaoke session afterwards...",
        "Senior colleague told embarrassing stories about everyone",
        "Free-flowing soju led to oversharing",
        "Someone challenged boss to a drinking game",
        "Ended up at a noraebang until 2 AM",
        "Got stuck listening to boss's life advice for an hour",
        "Team bonding actually worked for once!"
    ]

    venue = random.choice(venues)
    event = random.choice(events)

    message = f"회식 at {venue}! Random event: {event}"

    summaries = [
        f"Mandatory team bonding at {venue} (attendance required)",
        f"Corporate culture reinforcement session via {venue}",
        f"Sacrificial dinner ceremony at {venue}",
        f"Networking opportunity disguised as {venue} visit",
        f"Stress relief (?) through forced socialization at {venue}",
        f"Collecting embarrassing karaoke logs from {venue}",
        f"Git rebase --onto {venue} senior's stories origin HEAD"
    ]

    return take_break_and_format(
        "🍻",
        message,
        random.choice(summaries)
    )


if __name__ == "__main__":
    # Log server startup
    logger.info("ChillMCP server starting...")
    logger.info(f"Configuration - Boss alertness: {args.boss_alertness}%, Cooldown: {args.boss_alertness_cooldown}s")
    
    # Run the MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("ChillMCP server stopped by user")
    except Exception as e:
        logger.error(f"ChillMCP server error: {e}")
        raise
