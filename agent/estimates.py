"""Our estimates: reading and adding to estimates.csv (the team's own book).

The file only grows. To change an estimate, add a new row; the newest row for a
company, period and metric is the one that counts. The `method` column records where
each number came from (a consensus seed, the team's own work, or a revision after a release).

The made-up SAMPLE company's estimates live separately in samples/sample_estimates.csv
so practice runs never touch the real book.
"""

import csv

import pandas as pd

from agent.config import PROJECT_DIR
from agent.schemas import METRICS

ESTIMATES_FILE = PROJECT_DIR / "estimates.csv"
SAMPLE_ESTIMATES_FILE = PROJECT_DIR / "samples" / "sample_estimates.csv"
COLUMNS = ["ticker", "fiscal_year", "quarter", "metric", "estimate", "unit", "method"]


def estimates_file_for(ticker: str):
    return SAMPLE_ESTIMATES_FILE if ticker.upper() == "SAMPLE" else ESTIMATES_FILE


def load_estimate_rows(ticker: str, fiscal_year: int, quarter: int) -> dict[str, dict]:
    """Return {metric: {"estimate": value, "method": text}} for one company and period."""
    tables = [pd.read_csv(path) for path in (ESTIMATES_FILE, SAMPLE_ESTIMATES_FILE) if path.exists()]
    if not tables:
        return {}
    table = pd.concat(tables)
    rows = table[
        (table["ticker"].astype(str).str.upper() == ticker.upper())
        & (table["fiscal_year"] == fiscal_year)
        & (table["quarter"] == quarter)
        & table["estimate"].notna()
    ]
    found = {}
    for _, row in rows.iterrows():  # later rows replace earlier ones
        found[row["metric"]] = {"estimate": float(row["estimate"]), "method": str(row.get("method", ""))}
    return found


def load_estimates(ticker: str, fiscal_year: int, quarter: int) -> dict[str, float]:
    """Return {metric: estimate} for one company and period."""
    return {metric: row["estimate"] for metric, row in load_estimate_rows(ticker, fiscal_year, quarter).items()}


def append_estimates(rows: list[dict], path=None) -> None:
    """Add rows to the estimates file. Each row needs ticker, fiscal_year, quarter, metric, estimate, method."""
    if not rows:
        return
    path = path or estimates_file_for(rows[0]["ticker"])
    header = COLUMNS
    if path.exists():
        with open(path, encoding="utf-8") as file:
            header = next(csv.reader(file), COLUMNS)
        needs_newline = path.read_bytes()[-1:] not in (b"\n", b"")
    else:
        needs_newline = False
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as file:
        if needs_newline:
            file.write("\n")
        writer = csv.DictWriter(file, fieldnames=header, extrasaction="ignore")
        if is_new:
            writer.writeheader()
        for row in rows:
            writer.writerow({"unit": METRICS[row["metric"]]["unit"], **row})
