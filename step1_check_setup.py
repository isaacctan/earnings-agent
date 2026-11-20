"""STEP 1 - Check that your computer is ready.

Run it from the VS Code terminal with:   python step1_check_setup.py
"""

import sys

print("Checking your setup...\n")
problems = 0

# 1. Python version
version = sys.version_info
if version >= (3, 10):
    print(f"[OK]    Python {version.major}.{version.minor} is installed.")
else:
    print(f"[FIX]   Python {version.major}.{version.minor} is too old. Install 3.12 from python.org.")
    problems += 1

# 2. Virtual environment
if sys.prefix != sys.base_prefix:
    print("[OK]    The virtual environment (.venv) is active.")
else:
    print("[FIX]   The virtual environment is not active. See START_HERE.md, Part 3.")
    problems += 1

# 3. Packages
for package in ["requests", "bs4", "dotenv", "pandas", "streamlit", "anthropic", "pydantic", "yfinance"]:
    try:
        __import__(package)
        print(f"[OK]    Package '{package}' is installed.")
    except ImportError:
        print(f"[FIX]   Package '{package}' is missing. Run: pip install -r requirements.txt")
        problems += 1

# 4. The .env file
try:
    from agent.config import SetupError, get_anthropic_api_key, get_sec_user_agent

    try:
        get_sec_user_agent()
        print("[OK]    Your .env file has your name and email for the SEC.")
    except SetupError as error:
        print(f"[FIX]   {error}")
        problems += 1

    try:
        get_anthropic_api_key()
        print("[OK]    Your .env file has a Claude API key.")
    except SetupError:
        print("[NOTE]  No Claude API key yet. Steps 1-2 work without it; step 3 needs it (START_HERE.md, Part 6).")
except ImportError:
    pass  # already reported above as a missing package

print()
if problems == 0:
    print("All set! Next, run:   python step2_fetch_release.py AAPL   (then: python step3_run_agent.py --sample)")
else:
    print(f"{problems} thing(s) to fix. Fix them, then run this file again.")
