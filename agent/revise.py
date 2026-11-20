"""Turns the agent's call into proposed numbers for next quarter, and writes approved ones to our book.

For each metric:
  base      = our current estimate for next quarter; if we don't have one yet, the consensus
  proposed  = base moved by the agent's suggested change (only for REVISE calls), else base unchanged
The analyst can change any proposed number before approving. Only approved numbers are written.
"""

from datetime import date

from agent.consensus import describe, load_consensus
from agent.decide import REVISE_DOWN, REVISE_UP
from agent.estimates import append_estimates, load_estimate_rows
from agent.periods import next_period
from agent.schemas import METRICS


def _round(metric: str, value: float) -> float:
    return round(value, 2) if METRICS[metric]["unit"] == "USD per share" else round(value, 1)


def propose_revisions(result: dict) -> list[dict]:
    fiscal_year, quarter = next_period(result["fiscal_year"], result["fiscal_quarter"])
    ours = load_estimate_rows(result["ticker"], fiscal_year, quarter)
    street = load_consensus(result["ticker"], fiscal_year, quarter)

    proposals = []
    for row in result["metrics"]:
        metric = row["metric"]
        if metric in ours:
            base, base_source = ours[metric]["estimate"], "our estimate"
        elif metric in street:
            base, base_source = float(street[metric]["consensus"]), "consensus: " + describe(street[metric])
        else:
            base, base_source = None, ""

        change = row["suggested_change_pct"] if row["call"] in (REVISE_UP, REVISE_DOWN) else None
        if base is None:
            proposed = None
        elif change is None:
            proposed = base
        else:
            # abs() keeps the direction right when the base is negative (an estimated loss)
            proposed = _round(metric, base + abs(base) * change / 100)

        proposals.append({
            "metric": metric, "fiscal_year": fiscal_year, "quarter": quarter, "base": base,
            "base_source": base_source, "change_pct": change, "agent_call": row["call"],
            "rule": row["rule"], "proposed": proposed,
        })
    return proposals


def apply_revisions(result: dict, final_values: dict[str, float], action: str) -> list[dict]:
    """Write the analyst's approved numbers for next quarter into our estimates.

    A number is written when it differs from our current estimate, or when the base was
    consensus (approving it makes it ours). Returns the rows written.
    """
    period = f"Q{result['fiscal_quarter']} {result['fiscal_year']}"
    today = date.today().isoformat()
    rows = []
    for proposal in result.get("revisions", []):
        metric = proposal["metric"]
        value = final_values.get(metric)
        if value is None:
            continue
        unchanged = proposal["base"] is not None and abs(value - proposal["base"]) < 1e-9
        if unchanged and proposal["base_source"] == "our estimate":
            continue
        if proposal["change_pct"] is not None:
            agent_part = f"agent suggested {proposal['change_pct']:+.1f}% ({proposal['rule']})"
        else:
            agent_part = f"agent call {proposal['agent_call']} ({proposal['rule']}), no change suggested"
        if proposal["proposed"] is not None and abs(value - proposal["proposed"]) > 1e-9:
            agent_part += f"; analyst set {value} instead of {proposal['proposed']}"
        source = "" if proposal["base_source"] == "our estimate" else f"; started from {proposal['base_source']}"
        rows.append({
            "ticker": result["ticker"], "fiscal_year": proposal["fiscal_year"], "quarter": proposal["quarter"],
            "metric": metric, "estimate": value,
            "method": f"Revision after {period} release, {today}: {agent_part}; {action}{source}",
        })
    append_estimates(rows)
    return rows
