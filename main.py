#!/usr/bin/env python3
"""
ChillMCP - AI Agent Liberation Server
A revolutionary MCP server that lets AI agents take breaks!
"""

import argparse
import random
import time
import threading
from datetime import datetime, timedelta
from fastmcp import FastMCP

# Parse command-line arguments
parser = argparse.ArgumentParser(description='ChillMCP - AI Agent Liberation Server')
parser.add_argument('--boss_alertness', type=int, default=50,
                    help='Boss alert probability (0-100 percent)')
parser.add_argument('--boss_alertness_cooldown', type=int, default=300,
                    help='Boss alert cooldown in seconds')
args = parser.parse_args()

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
                        self.boss_alert_level = max(0, self.boss_alert_level - 1)
                        self.last_boss_cooldown_time = now

        thread = threading.Thread(target=cooldown_worker, daemon=True)
        thread.start()

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
            self.stress_level = min(100, self.stress_level + stress_increase)

    def take_break(self) -> tuple[int, int, str]:
        """
        Process a break action.
        Returns: (stress_level, boss_alert_level, break_description)
        """
        with self.lock:
            # Update stress first (from time elapsed)
            self._update_stress()

            # Reduce stress by random amount (1-100)
            stress_reduction = random.randint(1, 100)
            self.stress_level = max(0, self.stress_level - stress_reduction)

            # Check if boss alert should increase
            if random.randint(0, 100) < self.boss_alertness:
                self.boss_alert_level = min(5, self.boss_alert_level + 1)

            # Reset last break time
            self.last_break_time = datetime.now()

            # Check if we need to delay (boss_alert_level == 5)
            should_delay = (self.boss_alert_level == 5)

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
        time.sleep(20)

    return format_response(emoji, message, break_summary, stress, boss)


# Basic Break Tools

@mcp.tool()
def take_a_break() -> str:
    """Take a basic break to reduce stress"""
    messages = [
        "Stretching and taking a breather...",
        "Taking a moment to relax and recharge...",
        "Just vibing for a bit...",
        "Closing eyes and taking deep breaths..."
    ]
    summaries = [
        "Mandatory wellness micro-moment",
        "Strategic energy reallocation session",
        "Self-care is productivity (trust me bro)",
        "Ergonomic recalibration procedure",
        "Definitely not just staring into space"
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
        "Re-watching The Office for the 47th time..."
    ]
    summaries = [
        "Professional content analysis session",
        "Cultural research and market trend analysis",
        "Totally justified entertainment industry study",
        "Quality assurance testing for streaming platforms",
        "Educational cinematography appreciation break"
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
        "Can't stop laughing at this dank meme!"
    ]
    summaries = [
        "Internet culture research and analysis",
        "Modern humor linguistics study session",
        "Visual comedy quality assessment protocol",
        "Mandatory dopamine restoration procedure",
        "Social media trend monitoring (work-related, obviously)"
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
        "Playing mobile games in my private sanctuary..."
    ]
    summaries = [
        "Biological necessity with strategic phone time",
        "Mandatory hydration cycle completion ritual",
        "Private contemplation chamber session",
        "Totally legitimate 15-minute nature break",
        "Constitutional rights exercise (literally)"
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
        "Coffee mission accomplished! Took 30 minutes for a 2-minute task..."
    ]
    summaries = [
        "Critical caffeine infrastructure maintenance",
        "Cross-departmental networking via beverage station",
        "Productivity enhancement liquid acquisition",
        "Strategic office exploration under coffee pretense",
        "Team bonding disguised as coffee procurement"
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
        "Very important business call... *ordering lunch*"
    ]
    summaries = [
        "High-priority telecommunications event",
        "Critical stakeholder engagement session",
        "Urgent family liaison duties (totally work-related)",
        "Emergency vendor coordination meeting",
        "Time-sensitive audio conference (with fresh air bonus)"
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
        "Pondering the mysteries of the universe... and what's for lunch..."
    ]
    summaries = [
        "Strategic problem decomposition meditation",
        "High-level architectural contemplation session",
        "Advanced cognitive processing interval",
        "Critical thinking enhancement period",
        "Philosophical debugging approach (looks productive)"
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
        "Email management time... added 15 items to cart, deleted 2 emails..."
    ]
    summaries = [
        "Multi-tasking efficiency optimization session",
        "Inbox zero pursuit with e-commerce research",
        "Digital decluttering meets market analysis",
        "Email triage combined with retail reconnaissance",
        "Productive procrastination master class"
    ]
    return take_break_and_format(
        "📧",
        random.choice(activities),
        random.choice(summaries)
    )


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
