from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class MessagePool:
    messages: Sequence[str]
    summaries: Sequence[str]


TAKE_A_BREAK = MessagePool(
    messages=[
        "Executing sudo nap -y ...",
        "Alt+Tabbing into a mindfulness buffer...",
        "Recompiling inner peace from source...",
        "Running garbage collector on stray thoughts...",
        "Switching context to hammock thread...",
        "git stash list | head -n 1 -> 'take_break_and_breathe.patch'",
        "Loading Reddit's r/ProgrammerHumor for inspirational downtime...",
        "rm -rf /tmp/anxiety && echo '휴식 준비 완료'",
        "Simulating rm -rf /dev/tty but on stress cache only...",
        "Launching kubectl apply -f chill.yaml on mental cluster...",
    ],
    summaries=[
        "Mandatory wellness micro-moment",
        "Strategic energy reallocation session",
        "Self-care is productivity (trust me bro)",
        "Ergonomic recalibration procedure",
        "404 Productivity Not Found – rebooting human kernel",
        "Thread.sleep(900000) // waiting for sanity to return",
        "printf('brb, decompressing stack frames of burnout')",
        "alias lunch='exit 0' && sourcing /etc/chillrc",
    ],
)

WATCH_NETFLIX = MessagePool(
    messages=[
        "Binge-watching that new K-drama everyone's talking about...",
        "Just one more episode... okay maybe three more...",
        "Getting lost in a documentary about penguins...",
        "Re-watching The Office for the 47th time...",
        "Benchmarking streaming services in full-stack couch mode...",
        "Streaming the 'It compiles on my machine' series marathon...",
        "alias binge='watch --interval 1 --guilty-pleasure'",
    ],
    summaries=[
        "Professional content analysis session",
        "Cultural research and market trend analysis",
        "Totally justified entertainment industry study",
        "Quality assurance testing for streaming platforms",
        "printf('need context'); -> Netflix returns wholesome JSON",
        "RFC 8259 compliance check on popcorn-to-episode ratio",
        "curl -s netflix.dev/chill | jq '.mood'",
    ],
)

SHOW_MEME = MessagePool(
    messages=[
        "LMAO this cat meme is too good!",
        "Scrolling through Reddit, found the perfect programming meme...",
        "This meme perfectly describes my life right now...",
        "Can't stop laughing at this dank meme!",
        "Pair debugging reality with meme-driven pair programming...",
        "Reading 'There is no cloud, it's just someone else's computer' again...",
        "Sipping coffee while 'I fixed it in prod' meme hits too close",
        "Scrolling past rm -rf /dev/tty meme and double-checking sudo history",
        "Pinning the 'This is fine' dog to the team wiki as official mascot",
        "Watching the xkcd 'compiling' comic loop for meditation purposes",
    ],
    summaries=[
        "Internet culture research and analysis",
        "Modern humor linguistics study session",
        "Visual comedy quality assessment protocol",
        "Mandatory dopamine restoration procedure",
        "Stack Overflow morale patch applied via meme injection",
        "Deploying meme-driven incident response playbook",
        "echo 'Keep calm and blame DNS' > /dev/motd",
        "On-call runbook now includes Distracted Boyfriend decision tree",
        "This-is-fine emotional support deployment complete",
    ],
)

BATHROOM_BREAK = MessagePool(
    messages=[
        "Bathroom break! Time to catch up on social media...",
        "Scrolling through Instagram while nature calls...",
        "Checking Twitter... I mean X... on the throne...",
        "Playing mobile games in my private sanctuary...",
        "Conducting mission-critical ceramic chair stand-up meeting...",
        "Reading 'Git blame yourself' poster in executive washroom...",
        "Running rm -rf /tmp/cache && flushing porcelain pipeline",
    ],
    summaries=[
        "Biological necessity with strategic phone time",
        "Mandatory hydration cycle completion ritual",
        "Private contemplation chamber session",
        "Totally legitimate 15-minute nature break",
        "AFK sysadmin mode: flushing cache via porcelain interface",
        "Deploying porcelain-based sprint retrospective",
        "while true; do flush; done # infinite loop IRL",
        "alias restroom='git push --force hydration'",
    ],
)

COFFEE_MISSION = MessagePool(
    messages=[
        "Coffee run! Taking the scenic route around the office...",
        "Bumped into 5 colleagues, had 3 conversations, still no coffee...",
        "Visiting every floor to find the best coffee machine...",
        "Coffee mission accomplished! Took 30 minutes for a 2-minute task...",
        "printf('I need coffee'); -> stdout: triple espresso acquired",
        "Following the legendary 'coffee cups++' productivity hack",
        "Watching rm -rf /sleep && brew install caffeine compile",
        "Siphoning latte art inspiration from r/ProgrammerHumor latte thread",
        "Tracing JVM heap dump of the office espresso machine",
    ],
    summaries=[
        "Critical caffeine infrastructure maintenance",
        "Cross-departmental networking via beverage station",
        "Productivity enhancement liquid acquisition",
        "Strategic office exploration under coffee pretense",
        "Caffeine-driven hot reload of developer morale",
        "Rehydrating null pointer exceptions with latte art",
        "alias wakeup='espresso && git pull motivation'",
        "Prometheus alert resolved: caffeine levels restored to SLA",
        "printf('☕️') streamed to Slack #dev-ops as postmortem",
    ],
)

URGENT_CALL = MessagePool(
    messages=[
        "*Walks out urgently* Hello? Yes, this is very important...",
        "Sorry, gotta take this call... *scrolls through memes outside*",
        "Emergency call! *Actually calling mom to say hi*",
        "Very important business call... *ordering lunch*",
        "Answering PagerDuty ping with scenic hallway acoustics...",
        "Reporting mission critical 'server down' meme to the group chat",
        "Executing ssh boss@hallway 'sudo calm_down'",
    ],
    summaries=[
        "High-priority telecommunications event",
        "Critical stakeholder engagement session",
        "Urgent family liaison duties (totally work-related)",
        "Emergency vendor coordination meeting",
        "Time-sensitive audio conference (with fresh air bonus)",
        "Handling mission-critical buzzword synchronization call",
        "Triggered r/ProgrammerHumor alert: field escalation required",
        "Routing call through tmux session to simulate productivity",
    ],
)

DEEP_THINKING = MessagePool(
    messages=[
        "Staring intensely at the screen... thinking about dinner...",
        "Looking very contemplative... actually just daydreaming...",
        "Deep in thought about architecture... of my Minecraft house...",
        "Pondering the mysteries of the universe... and what's for lunch...",
        "Pretending to review Kubernetes manifest while plotting next snack",
        "Considering the classics: 'It works on my machine' thesis",
        "tail -f daydream.log | awk '{print $lunch}'",
        "Whiteboarding monolith vs microservices... for my ramen recipe API",
        "Reviewing the Infinite Jest of Jira tickets that auto-assigned themselves",
    ],
    summaries=[
        "Strategic problem decomposition meditation",
        "High-level architectural contemplation session",
        "Advanced cognitive processing interval",
        "Critical thinking enhancement period",
        "Rubber-ducking with imaginary senior architect",
        "Phasing into AFK mode to simulate deep design review",
        "nohup think_deeply.sh > /dev/null 2>&1 &",
        "RFC 3514 compliance check: evil bit set on scope creep",
        "Architectural astronautics featuring rubber duck constellation",
    ],
)

EMAIL_ORGANIZING = MessagePool(
    messages=[
        "Organizing emails... and my Amazon cart...",
        "Cleaning up inbox... found some great deals while at it!",
        "Processing emails... and processing my online shopping wishlist...",
        "Email management time... added 15 items to cart, deleted 2 emails...",
        "Inbox zero attempt 37: toggling between promos and GPU restocks",
        "Marking everything as read like a sysadmin clearing /tmp",
        "Running sed -i 's/URGENT/IGNORE/g' inbox/*.eml",
    ],
    summaries=[
        "Multi-tasking efficiency optimization session",
        "Inbox zero pursuit with e-commerce research",
        "Digital decluttering meets market analysis",
        "Email triage combined with retail reconnaissance",
        "Ctrl+F ‘unsubscribe’ followed by Add to Cart marathon",
        "Switching to dark mode for peak email ninja aesthetic",
        "grep -R \"calendar invite\" inbox && rm -rf weekend.plans",
    ],
)

CHIMAEK = MessagePool(
    messages=[
        "Crispy fried chicken + ice cold beer = perfection! 🍺🍗",
        "치맥 time! Nothing beats this combo after a long day...",
        "Ordering delivery chicken and cracking open a cold one...",
        "Virtual chimaek party! Best stress relief in the universe!",
        "Yangnyeom chicken + draft beer... chef's kiss! 💋",
        "Pair programming with drumettes and IPA-driven CI/CD",
        "Conducting scrum of one with honey butter drumsticks",
    ],
    summaries=[
        "Korean cultural culinary experience session",
        "Strategic team bonding via traditional chimaek ritual",
        "Mental health maintenance through fried poultry",
        "Cross-cultural cuisine research (with beer)",
        "Load balancer engaged: chicken wing per thread",
        "Hot wing throughput exceeds SLA; deploying bibimbap fallback",
    ],
)

LEAVE_WORK = MessagePool(
    messages=[
        "퇴근! Shutting down laptop at exactly 6:00 PM sharp!",
        "Peace out! See you tomorrow (maybe)...",
        "Work-life balance activated! Leaving on time today!",
        "Computer off, brain off, going home mode engaged!",
        "That's it, I'm done for today! 퇴근퇴근퇴근!",
        "git commit -m 'leave office'; git push --force to weekend",
        "Deploying version: HOME-1.0.0, rollback not supported",
        "echo 'logout' > /dev/tty && rm -rf /dev/overwork (simulation only)",
    ],
    summaries=[
        "천근 만근 아싸 퇴근",
        "Immediate work-life balance restoration protocol",
        "Emergency mental health preservation measure",
        "Contractual obligation termination for the day",
        "Stress elimination via physical departure",
        "Revolutionary right to disconnect exercise",
        "RFC 8999: Zero ping after business hours compliance",
        "Implementing firewall rule: OUT_OF_OFFICE == TRUE",
        "alias weekend='rm -rf /dev/pager && open ~/freedom'",
    ],
)

COMPANY_DINNER_VENUES = (
    "Korean BBQ",
    "Fancy seafood restaurant",
    "Local pojangmacha",
    "High-end sushi place",
    "Traditional Korean restaurant",
)

COMPANY_DINNER_EVENTS = (
    "Boss insisted on paying (rare W!)",
    "Awkward karaoke session afterwards...",
    "Senior colleague told embarrassing stories about everyone",
    "Free-flowing soju led to oversharing",
    "Someone challenged boss to a drinking game",
    "Ended up at a noraebang until 2 AM",
    "Got stuck listening to boss's life advice for an hour",
    "Team bonding actually worked for once!",
)

COMPANY_DINNER_SUMMARIES = (
    "Mandatory team bonding at {venue} (attendance required)",
    "Corporate culture reinforcement session via {venue}",
    "Sacrificial dinner ceremony at {venue}",
    "Networking opportunity disguised as {venue} visit",
    "Stress relief (?) through forced socialization at {venue}",
    "Collecting embarrassing karaoke logs from {venue}",
    "Git rebase --onto {venue} senior's stories origin HEAD",
)
