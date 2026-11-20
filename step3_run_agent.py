"""STEP 3 - Run the whole agent on one earnings release.

    python step3_run_agent.py --sample              the built-in practice release (made-up company)
    python step3_run_agent.py AAPL                    the newest release for a ticker, from the SEC
    python step3_run_agent.py AAPL 2026-MM-DD       a specific release, by a filing date from step 2's list
    python step3_run_agent.py --file redteam/injection_FICTIONAL.txt --ticker SAMPLE

Needs ANTHROPIC_API_KEY in your .env file. Each run costs a few cents.
"""

import sys
from pathlib import Path

from agent.config import PROJECT_DIR, RUNS_DIR, SetupError
from agent.pipeline import run_on_filing, run_on_text


def main() -> None:
    args = sys.argv[1:]
    try:
        if "--sample" in args:
            path = PROJECT_DIR / "samples" / "sample_release_FICTIONAL.txt"
            result = run_on_text("SAMPLE", path.stem, path.read_text(encoding="utf-8"), str(path))
        elif "--file" in args:
            path = Path(args[args.index("--file") + 1])
            ticker = args[args.index("--ticker") + 1] if "--ticker" in args else "SAMPLE"
            result = run_on_text(ticker, path.stem, path.read_text(encoding="utf-8"), str(path))
        elif args:
            result = run_on_filing(args[0], args[1] if len(args) > 1 else None)
        else:
            print(__doc__)
            return
    except SetupError as error:
        print(f"\nSomething needs fixing:\n  {error}")
        return

    print(result["note"])
    print(f"\nSaved to {RUNS_DIR / (result['ticker'] + '_' + result['release_date'] + '.md')}")


if __name__ == "__main__":
    main()
