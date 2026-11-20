"""Agent step 6: write the analyst note.

The note is assembled by code from facts already checked. Claude does not write
it, so it cannot contain a number or claim that wasn't verified upstream.
"""

from agent.schemas import METRICS


def _fmt(value, unit: str) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.2f}" if unit == "USD per share" else f"${value:,.1f}M"


def build_note(result: dict) -> str:
    period = f"Q{result['fiscal_quarter']} {result['fiscal_year']}"
    overall = result["overall"]
    lines = [
        f"# {result['company_name']} ({result['ticker']}) - {period} earnings: {overall['call']}",
        "",
        f"**Confidence:** {overall['confidence']}  |  **Why:** {overall['reason']} (rule {overall['rule']})",
        "",
        "> Draft produced by the Earnings Revision Agent. Not final until an analyst approves it.",
        "",
        "## Reported vs. our estimates",
        "",
        "| Metric | Our estimate | Consensus | Reported | vs. ours | vs. consensus | Call | Suggested change |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in result["metrics"]:
        unit = METRICS[row["metric"]]["unit"]
        pct = f"{row['pct']:+.1f}%" if row["pct"] is not None else "n/a"
        street_pct = f"{row['consensus_pct']:+.1f}%" if row.get("consensus_pct") is not None else "n/a"
        change = f"{row['suggested_change_pct']:+.1f}%" if row["suggested_change_pct"] is not None else "-"
        lines.append(
            f"| {METRICS[row['metric']]['label']} | {_fmt(row['estimate'], unit)} | "
            f"{_fmt(row.get('consensus'), unit)} | {_fmt(row['actual'], unit)} | {pct} | {street_pct} | "
            f"{row['call']} | {change} |"
        )

    lines += ["", "## What drove the variances", ""]
    drivers = [row for row in result["metrics"] if row.get("driver_explanation")]
    if not drivers:
        lines.append("No variances were large enough to need an explanation.")
    for row in drivers:
        lines.append(f"- **{METRICS[row['metric']]['label']}** ({row['driver_kind'].replace('_', '-')}): {row['driver_explanation']}")
        if row["driver_quote"]:
            lines.append(f"  - Source: \"{row['driver_quote']}\"")

    guidance = result["guidance"]
    lines += ["", "## Guidance", "", f"**{guidance['status'].replace('_', ' ').title()}.** {guidance['summary']}".strip()]
    if guidance["source_quote"]:
        lines.append(f"- Source: \"{guidance['source_quote']}\"")

    revisions = [r for r in result.get("revisions", []) if r["base"] is not None]
    if revisions:
        first = revisions[0]
        lines += ["", f"## Proposed estimates for Q{first['quarter']} {first['fiscal_year']}", "",
                  "| Metric | Current | Starting point | Proposed |", "|---|---|---|---|"]
        for r in revisions:
            unit = METRICS[r["metric"]]["unit"]
            source = "ours" if r["base_source"] == "our estimate" else "consensus"
            lines.append(f"| {METRICS[r['metric']]['label']} | {_fmt(r['base'], unit)} | {source} | {_fmt(r['proposed'], unit)} |")
        lines.append("")
        lines.append("Nothing is written to our estimates until an analyst approves these numbers.")

    lines += ["", "## Check before approving", ""]
    if result["flags"]:
        lines += [f"- {flag}" for flag in result["flags"]]
    else:
        lines.append("- Nothing flagged.")

    lines += ["", "## Where each number came from", ""]
    for row in result["metrics"]:
        if row["source_quote"]:
            mark = "verified" if row["verified"] else "NOT VERIFIED"
            lines.append(f"- {METRICS[row['metric']]['label']} ({mark}): \"{row['source_quote']}\"")
    lines += ["", f"Source document: {result['source']}"]
    return "\n".join(lines)
