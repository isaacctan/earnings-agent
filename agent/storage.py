"""Saves what the agent did and what the analyst decided. Files only grow; nothing is overwritten
except a re-run of the same company and date."""

import csv
import json
from datetime import datetime

from agent.config import PROJECT_DIR, RUNS_DIR

RUN_LOG = PROJECT_DIR / "data" / "run_log.csv"
DECISIONS_LOG = PROJECT_DIR / "data" / "decisions.csv"


def _append_row(path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(row))
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def save_run(result: dict) -> None:
    """Save the full result (.json), the note (.md), and one line in the run log."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{result['ticker']}_{result['release_date']}"
    (RUNS_DIR / f"{name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (RUNS_DIR / f"{name}.md").write_text(result["note"], encoding="utf-8")
    _append_row(RUN_LOG, {
        "run_at": result["run_at"],
        "ticker": result["ticker"],
        "release_date": result["release_date"],
        "overall_call": result["overall"]["call"],
        "confidence": result["overall"]["confidence"],
        "flags": len(result["flags"]),
        "model": result["model"],
    })


def load_run(ticker: str, release_date: str) -> dict | None:
    path = RUNS_DIR / f"{ticker}_{release_date}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def record_decision(result: dict, action: str, comment: str) -> None:
    """Record what the analyst did with the agent's recommendation."""
    _append_row(DECISIONS_LOG, {
        "decided_at": datetime.now().isoformat(timespec="seconds"),
        "ticker": result["ticker"],
        "release_date": result["release_date"],
        "agent_call": result["overall"]["call"],
        "analyst_action": action,
        "comment": comment,
    })
