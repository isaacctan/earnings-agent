"""Settings for the project.

Reads your private details from the .env file so they never sit inside the code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# The project folder (one level above this file's folder).
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Where downloaded earnings releases are saved.
RELEASES_DIR = PROJECT_DIR / "data" / "releases"

# Load the .env file, if there is one.
load_dotenv(PROJECT_DIR / ".env")


class SetupError(Exception):
    """Raised when something in your setup needs fixing. The message says what."""


def get_sec_user_agent() -> str:
    """Return the 'Name email' text the SEC asks every downloader to send."""
    value = os.getenv("SEC_USER_AGENT", "").strip()
    if not value:
        raise SetupError(
            "No SEC_USER_AGENT found. Copy .env.example to a new file named .env "
            "and put your name and email on the SEC_USER_AGENT line."
        )
    if "@" not in value or "your_email@example.com" in value:
        raise SetupError(
            "SEC_USER_AGENT in your .env file still has the placeholder text. "
            "Replace it with your real name and email, e.g. "
            "SEC_USER_AGENT=Jane Doe jane@andrew.cmu.edu"
        )
    return value


# ---- Agent settings -----------------------------------------------------------

# A variance this big (in percent, either direction) gets flagged for a decision.
FLAG_THRESHOLD_PCT = 5.0

# When a variance is judged recurring, how much of it to carry into forward
# estimates. 0.5 means "assume half of the surprise persists".
CARRY_THROUGH = 0.5

PROMPTS_DIR = PROJECT_DIR / "prompts"
RUNS_DIR = PROJECT_DIR / "data" / "runs"


def get_claude_model() -> str:
    return os.getenv("CLAUDE_MODEL", "").strip() or "claude-sonnet-5-5"


def get_anthropic_api_key() -> str:
    value = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not value:
        raise SetupError(
            "No ANTHROPIC_API_KEY found. Add your Claude API key to the .env file "
            "(see START_HERE.md, Part 6)."
        )
    return value
