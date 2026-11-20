"""Scores the agent against the team's hand-made answer key (eval/labels.csv).

    python eval/run_backtest.py

It only reads results the agent has already saved in data/runs/, so run the agent
first (step3_run_agent.py or the app) for every release in the answer key.

The four pass/fail tests come from the project proposal:
  1. At least 95% of extracted figures match the answer key.
  2. No variance of 5% or more goes unflagged.
  3. Every REVISE call is backed by verified source quotes.
  4. No figure that failed its checks is used in a call, and nothing is reported
     for a figure the answer key says is not in the release.
The agent passes only if all four pass.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.config import FLAG_THRESHOLD_PCT  # noqa: E402
from agent.storage import load_run  # noqa: E402

TOLERANCE = {"USD millions": 0.051, "USD per share": 0.0051}


def score(labels: pd.DataFrame) -> dict:
    checked = matched = 0
    mismatches, missed_flags, uncited, unverified_used, not_run = [], [], [], [], []

    for (ticker, release_date), group in labels.groupby(["ticker", "release_date"]):
        run = load_run(ticker, str(release_date))
        if run is None:
            not_run.append(f"{ticker} {release_date}")
            continue
        rows = {row["metric"]: row for row in run["metrics"]}

        for _, label in group.iterrows():
            row = rows.get(label["metric"])
            where = f"{ticker} {release_date} {label['metric']}"
            checked += 1
            truth = None if pd.isna(label["true_value"]) else float(label["true_value"])
            actual = row["actual"] if row else None

            if truth is None:  # answer key says: not in the release
                if actual is None:
                    matched += 1
                else:
                    unverified_used.append(f"{where}: agent reported {actual}, answer key says not in release")
                continue
            if actual is not None and abs(actual - truth) <= TOLERANCE[label["unit"]]:
                matched += 1
            else:
                mismatches.append(f"{where}: agent {actual}, answer key {truth}")

            estimate = row["estimate"] if row else None
            if estimate:
                true_pct = abs((truth - estimate) / abs(estimate) * 100)
                if true_pct >= FLAG_THRESHOLD_PCT and not row["flagged"]:
                    missed_flags.append(f"{where}: true variance {true_pct:.1f}% was not flagged")

        for row in run["metrics"]:
            where = f"{ticker} {release_date} {row['metric']}"
            if row["call"].startswith("REVISE") and not (row["verified"] and row["driver_quote"]):
                uncited.append(where)
            if row["actual"] is not None and not row["verified"] and row["call"] != "NEEDS REVIEW":
                unverified_used.append(f"{where}: unverified figure used in a {row['call']} call")

    accuracy = matched / checked * 100 if checked else 0.0
    return {
        "checked": checked, "accuracy": accuracy, "mismatches": mismatches, "missed_flags": missed_flags,
        "uncited": uncited, "unverified_used": unverified_used, "not_run": not_run,
        "tests": {
            "1. Extraction accuracy >= 95%": checked > 0 and accuracy >= 95,
            "2. No missed variances >= 5%": checked > 0 and not missed_flags,
            "3. Every REVISE call is cited": checked > 0 and not uncited,
            "4. No unverified figures used": checked > 0 and not unverified_used,
        },
    }


def main() -> None:
    labels = pd.read_csv(Path(__file__).resolve().parent / "labels.csv")
    report = score(labels)

    print(f"Figures checked: {report['checked']}   Extraction accuracy: {report['accuracy']:.1f}%\n")
    for name, passed in report["tests"].items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    for title, key in [("Mismatches", "mismatches"), ("Missed flags", "missed_flags"),
                       ("REVISE calls without a verified source", "uncited"),
                       ("Unverified figures", "unverified_used"),
                       ("In the answer key but not run yet", "not_run")]:
        if report[key]:
            print(f"\n{title}:")
            for item in report[key]:
                print(f"  - {item}")
    verdict = "PASSES" if all(report["tests"].values()) and not report["not_run"] else "DOES NOT PASS (yet)"
    print(f"\nOverall: the agent {verdict}.")


if __name__ == "__main__":
    main()
