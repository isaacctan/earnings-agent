"""STEP 4 - Pull Wall Street consensus estimates and seed our estimates with them.

    python step4_pull_consensus.py AAPL              one company
    python step4_pull_consensus.py --all           every company in companies.csv
    python step4_pull_consensus.py AAPL --no-seed    save consensus only; don't touch estimates.csv

What it does:
  1. Downloads consensus EPS and revenue from Yahoo Finance and saves it in data/consensus.csv.
  2. "Seeds" estimates.csv: copies consensus in ONLY where we have no estimate yet.
     Our existing estimates are never changed. After this, our estimates are ours: they move
     when we approve revisions after a release, not when the Street moves.
"""

import sys

import pandas as pd

from agent.config import PROJECT_DIR, SetupError
from agent.consensus import pull_consensus, save_consensus, seed_estimates


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    tickers = list(pd.read_csv(PROJECT_DIR / "companies.csv")["ticker"]) if "--all" in args else [args[0]]
    seed = "--no-seed" not in args

    for ticker in tickers:
        print(f"\n{ticker.upper()}")
        try:
            rows = pull_consensus(ticker)
        except SetupError as error:
            print(f"  Skipped: {error}")
            continue
        save_consensus(rows)
        for row in sorted(rows, key=lambda r: (r["fiscal_year"], r["quarter"], r["metric"])):
            analysts = f", {int(row['analysts'])} analysts" if row["analysts"] else ""
            print(f"  Q{row['quarter']} {row['fiscal_year']}  {row['metric']:<12} {row['consensus']:>12,.2f}  "
                  f"({row['kind']}, basis: {row['basis']}{analysts})")
        if any(r["metric"] == "diluted_eps" and r["basis"] != "gaap" for r in rows):
            print("  WARNING: some EPS consensus is not on a GAAP basis. Compare with care.")
        if seed:
            added = seed_estimates(rows)
            print(f"  Added {len(added)} row(s) to estimates.csv where we had no estimate.")

    print("\nSaved to data/consensus.csv.")
    print("Check: does the revenue consensus look like the 'Total revenue' line in a recent release?")
    print("Providers sometimes define revenue differently. If it doesn't match, fix those rows in estimates.csv.")


if __name__ == "__main__":
    main()
