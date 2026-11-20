"""Wall Street consensus estimates, pulled from Yahoo Finance (through the yfinance package).

What Yahoo offers for free, and how this file uses it:
  - EPS consensus for the next two quarters ("forward")
  - EPS consensus as it stood just before each of the last four reports ("historical")
  - Revenue consensus for the next two quarters
Both EPS series are requested on a GAAP basis, to match what the agent extracts.
Nothing free covers operating income or net income; those stay team-built.

Pulled numbers are stored in data/consensus.csv and never edited. That file is the
record of what the Street expected. Our own estimates live in estimates.csv:
"seeding" copies consensus into it only where we have no number yet, and after
that our estimates move on their own when we revise them.
"""

import csv
from datetime import date

import pandas as pd

from agent.config import PROJECT_DIR, SetupError
from agent.estimates import append_estimates, load_estimate_rows
from agent.periods import fiscal_period, month_end, quarter_end_after

CONSENSUS_FILE = PROJECT_DIR / "data" / "consensus.csv"
SAMPLE_CONSENSUS_FILE = PROJECT_DIR / "samples" / "sample_consensus.csv"
SOURCE = "Yahoo Finance"
FIELDS = ["pulled_at", "ticker", "fiscal_year", "quarter", "period_end", "metric", "consensus",
          "low", "high", "analysts", "unit", "basis", "kind", "source"]
SEEDED_METRICS = ["diluted_eps", "revenue"]


def _num(value) -> float | None:
    try:
        return None if value is None or pd.isna(value) else float(value)
    except (TypeError, ValueError):
        return None


def _basis(table) -> str:
    """Which EPS basis Yahoo says it returned: gaap, adjusted, or unknown."""
    if table is None or table.empty or "methodology" not in table.columns:
        return "unknown"
    label = str(table["methodology"].iloc[0]).lower()
    return {"gaap": "gaap", "normalized": "adjusted"}.get(label, "unknown")


def _in_usd(table) -> bool:
    return table is None or table.empty or "currency" not in table.columns or table["currency"].iloc[0] in (None, "USD")


def rows_from_yahoo(ticker: str, fye_month: int, history, eps_estimate, revenue_estimate, pulled_at: str) -> list[dict]:
    """Turn Yahoo's tables into rows for data/consensus.csv. No downloading happens here."""
    rows = []

    def add(period_end, metric, value, low, high, analysts, unit, basis, kind):
        if value is None:
            return
        fiscal_year, quarter = fiscal_period(period_end, fye_month)
        rows.append({
            "pulled_at": pulled_at, "ticker": ticker.upper(), "fiscal_year": fiscal_year, "quarter": quarter,
            "period_end": period_end.isoformat(), "metric": metric, "consensus": value, "low": low,
            "high": high, "analysts": analysts, "unit": unit, "basis": basis, "kind": kind, "source": SOURCE,
        })

    # Historical: the consensus just before each recent report. Also tells us which quarter was reported last.
    last_reported = None
    if history is not None and not history.empty and "epsEstimate" in history.columns and _in_usd(history):
        basis = _basis(history)
        for when, row in history.sort_index().iterrows():
            end = month_end(when)
            add(end, "diluted_eps", _num(row.get("epsEstimate")), None, None, None, "USD per share", basis, "historical")
            if _num(row.get("epsActual")) is not None:
                last_reported = end
    if last_reported is None:
        return rows  # without it we can't tell which fiscal quarter "0q" is

    # Forward: "0q" is the quarter after the last one reported, "+1q" the one after that.
    for label, quarters_ahead in (("0q", 1), ("+1q", 2)):
        end = quarter_end_after(last_reported, quarters_ahead)
        if eps_estimate is not None and label in eps_estimate.index and _in_usd(eps_estimate):
            row = eps_estimate.loc[label]
            add(end, "diluted_eps", _num(row.get("avg")), _num(row.get("low")), _num(row.get("high")),
                _num(row.get("numberOfAnalysts")), "USD per share", _basis(eps_estimate), "forward")
        if revenue_estimate is not None and label in revenue_estimate.index and _in_usd(revenue_estimate):
            row = revenue_estimate.loc[label]

            def millions(value):
                value = _num(value)
                return None if value is None else round(value / 1_000_000, 3)

            add(end, "revenue", millions(row.get("avg")), millions(row.get("low")), millions(row.get("high")),
                _num(row.get("numberOfAnalysts")), "USD millions", "provider-defined", "forward")
    return rows


def fetch_from_yahoo(ticker: str, fye_month: int) -> list[dict]:
    """Download consensus for one ticker. Asks for GAAP EPS first and falls back to Yahoo's default."""
    import yfinance as yf

    stock = yf.Ticker(ticker.upper())
    try:
        history = stock.get_earnings_history(methodology="gaap")
        if history is None or history.empty:
            history = stock.get_earnings_history()
        eps_estimate = stock.get_earnings_estimate(methodology="gaap")
        if eps_estimate is None or eps_estimate.empty:
            eps_estimate = stock.get_earnings_estimate()
        revenue_estimate = stock.get_revenue_estimate()
    except Exception as error:  # yfinance raises many kinds of errors when Yahoo changes or is unreachable
        raise SetupError(
            f"Couldn't get consensus for {ticker.upper()} from Yahoo Finance ({type(error).__name__}: {error}). "
            "Check you're online, then try `pip install --upgrade yfinance`. If it still fails, "
            "enter estimates by hand in estimates.csv."
        )
    rows = rows_from_yahoo(ticker, fye_month, history, eps_estimate, revenue_estimate, date.today().isoformat())
    if not rows:
        raise SetupError(
            f"Yahoo Finance returned no usable estimates for {ticker.upper()}. Small companies sometimes "
            "have little or no analyst coverage. Enter estimates by hand in estimates.csv."
        )
    return rows


def pull_consensus(ticker: str) -> list[dict]:
    """Look up the company's fiscal year end at the SEC, then download consensus from Yahoo."""
    from agent.sec_client import fiscal_year_end_month, ticker_to_cik

    cik, _ = ticker_to_cik(ticker)
    return fetch_from_yahoo(ticker, fiscal_year_end_month(cik))


def save_consensus(rows: list[dict], path=None) -> None:
    """Append pulled rows to data/consensus.csv (a growing record; nothing is overwritten)."""
    path = path or CONSENSUS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


def _pick_best(table: pd.DataFrame) -> pd.DataFrame:
    """One row per period and metric: the pre-report (historical) figure if there is one, else the latest pull."""
    if table.empty:
        return table
    table = table.assign(_historical=(table["kind"] == "historical"))
    table = table.sort_values(["_historical", "pulled_at"])
    return table.groupby(["ticker", "fiscal_year", "quarter", "metric"], as_index=False).tail(1).drop(columns="_historical")


def load_consensus(ticker: str, fiscal_year: int, quarter: int) -> dict[str, dict]:
    """Return {metric: consensus row} for one company and period."""
    tables = [pd.read_csv(path) for path in (CONSENSUS_FILE, SAMPLE_CONSENSUS_FILE) if path.exists()]
    if not tables:
        return {}
    table = pd.concat(tables)
    table = table[
        (table["ticker"].astype(str).str.upper() == ticker.upper())
        & (table["fiscal_year"] == fiscal_year)
        & (table["quarter"] == quarter)
    ]
    return {row["metric"]: row.to_dict() for _, row in _pick_best(table).iterrows()}


def describe(row: dict) -> str:
    """Short description of where a consensus number came from, for the method column."""
    parts = [row["source"]]
    if row["metric"] == "diluted_eps":
        parts.append({"gaap": "GAAP EPS", "adjusted": "ADJUSTED (non-GAAP) EPS"}.get(row["basis"], "EPS basis unknown"))
    else:
        parts.append("provider's revenue definition")
    if _num(row.get("analysts")):
        parts.append(f"{int(float(row['analysts']))} analysts")
    parts.append("pre-report" if row["kind"] == "historical" else "forward")
    parts.append(f"pulled {row['pulled_at']}")
    return ", ".join(parts)


def seed_estimates(rows: list[dict]) -> list[dict]:
    """Copy consensus into estimates.csv wherever the team has no estimate yet.

    Never replaces a team estimate. Returns the rows it added.
    """
    table = _pick_best(pd.DataFrame(rows)) if rows else pd.DataFrame()
    added = []
    for _, row in table.iterrows():
        if row["metric"] not in SEEDED_METRICS:
            continue
        existing = load_estimate_rows(row["ticker"], int(row["fiscal_year"]), int(row["quarter"]))
        if row["metric"] in existing:
            continue
        added.append({
            "ticker": row["ticker"], "fiscal_year": int(row["fiscal_year"]), "quarter": int(row["quarter"]),
            "metric": row["metric"], "estimate": row["consensus"],
            "method": "Consensus seed: " + describe(row.to_dict()),
        })
    append_estimates(added)
    return added
