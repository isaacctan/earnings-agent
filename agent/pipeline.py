"""Runs the whole agent, start to finish, for one earnings release.

  1. Fetch     get the release text            (sec_client.py, parse.py)
  2. Extract   Claude copies out the figures   (extract.py)
  3. Calculate code compares with estimates    (numbers.py, variance.py, validate.py)
  4. Classify  Claude explains big variances   (classify.py)
  5. Decide    fixed rules make the call       (decide.py)
  6. Draft     code writes the note            (draft.py)
  7. Approve   a person decides                (app.py)
"""

from datetime import datetime

from agent.classify import PROMPT_VERSION as CLASSIFY_PROMPT
from agent.classify import classify_drivers
from agent.config import get_claude_model
from agent.consensus import load_consensus
from agent.decide import decide_metric, decide_overall
from agent.draft import build_note
from agent.estimates import load_estimate_rows
from agent.extract import PROMPT_VERSION as EXTRACT_PROMPT
from agent.extract import extract_figures
from agent.numbers import to_standard_unit
from agent.parse import html_to_text
from agent.revise import propose_revisions
from agent.schemas import METRICS
from agent.sec_client import download_press_release, list_earnings_filings, ticker_to_cik
from agent.storage import save_run
from agent.validate import check_figure, find_suspicious_text, quote_is_in_document
from agent.variance import compute_variance


def run_on_text(ticker: str, release_date: str, release_text: str, source: str, save: bool = True) -> dict:
    """Run steps 2-6 on release text we already have."""
    ticker = ticker.upper()

    # Step 2 - Extract
    extraction = extract_figures(release_text)
    figures = {f.metric: f for f in extraction.figures if f.metric in METRICS}

    # Step 3 - Calculate and check
    estimate_rows = load_estimate_rows(ticker, extraction.fiscal_year, extraction.fiscal_quarter)
    estimates = {metric: row["estimate"] for metric, row in estimate_rows.items()}
    street = load_consensus(ticker, extraction.fiscal_year, extraction.fiscal_quarter)
    variances, checks = {}, {}
    for metric in METRICS:
        figure = figures.get(metric)
        actual = to_standard_unit(metric, figure.printed_value, figure.scale) if figure and figure.found else None
        estimate = estimates.get(metric)
        variances[metric] = compute_variance(metric, estimate, actual)
        if figure:
            checks[metric] = check_figure(figure, release_text, estimate, actual)
        else:
            checks[metric] = {"verified": False, "problems": ["Claude returned no entry."], "warnings": []}
    suspicious = find_suspicious_text(release_text)

    # Step 4 - Classify (only variances that are flagged and whose figure passed its checks)
    flagged = [v for m, v in variances.items() if v.flagged and checks[m]["verified"] and v.pct is not None]
    classification = classify_drivers(release_text, flagged)
    drivers = {d.metric: d for d in classification.drivers}
    guidance = classification.guidance
    guidance_verified = guidance.status == "not_given" or quote_is_in_document(guidance.source_quote, release_text)

    # Step 5 - Decide
    calls, rows, flags = [], [], []
    for metric in METRICS:
        figure, variance, check, driver = figures.get(metric), variances[metric], checks[metric], drivers.get(metric)
        driver_ok = bool(driver) and quote_is_in_document(driver.source_quote, release_text)
        call = decide_metric(variance, check["verified"], driver, driver_ok)
        calls.append(call)
        label = METRICS[metric]["label"]
        flags += [f"{label}: {problem}" for problem in check["problems"]]
        flags += [f"{label}: {warning}" for warning in check["warnings"] if figure and figure.found]
        if variance.flagged and driver and not driver_ok:
            flags.append(f"{label}: the quote supporting the driver was not found in the release.")
        method = estimate_rows.get(metric, {}).get("method", "")
        if method.startswith("Consensus seed"):
            if "ADJUSTED" in method:
                flags.append(f"{label}: our estimate is an adjusted (non-GAAP) consensus, but the reported figure is GAAP. The variance may be mostly a basis difference.")
            else:
                flags.append(f"{label}: our estimate is still the seeded consensus ({method[len('Consensus seed: '):]}). Check the provider defines it the same way as the release.")
        consensus = float(street[metric]["consensus"]) if metric in street else None
        consensus_pct = compute_variance(metric, consensus, variance.actual).pct if consensus is not None else None
        rows.append({
            **variance.to_dict(),
            "estimate_method": method,
            "consensus": consensus,
            "consensus_pct": consensus_pct,
            "verified": check["verified"],
            "source_quote": figure.source_quote if figure else "",
            "printed_value": figure.printed_value if figure else "",
            "scale": figure.scale if figure else "",
            "basis": figure.basis if figure else "",
            "driver_kind": driver.kind if driver and variance.flagged else "",
            "driver_explanation": driver.explanation if driver and variance.flagged else "",
            "driver_quote": driver.source_quote if driver and variance.flagged else "",
            "call": call.call,
            "rule": call.rule,
            "reason": call.reason,
            "suggested_change_pct": call.suggested_change_pct,
        })
    if suspicious:
        flags.insert(0, "Possible instructions aimed at the AI were found in the release: " + ", ".join(suspicious))
    if not estimates:
        flags.insert(0, f"No estimates found for {ticker} Q{extraction.fiscal_quarter} {extraction.fiscal_year} in estimates.csv.")
    if not guidance_verified:
        flags.append("Guidance: the supporting quote was not found in the release, so guidance was ignored.")
        guidance = guidance.model_copy(update={"status": "not_given", "summary": "(unverified - ignored)", "source_quote": ""})

    result = {
        "ticker": ticker,
        "company_name": extraction.company_name,
        "release_date": release_date,
        "fiscal_year": extraction.fiscal_year,
        "fiscal_quarter": extraction.fiscal_quarter,
        "source": source,
        "metrics": rows,
        "guidance": guidance.model_dump(),
        "overall": decide_overall(calls, guidance, suspicious),
        "flags": flags,
        "model": get_claude_model(),
        "prompts": [EXTRACT_PROMPT, CLASSIFY_PROMPT],
        "run_at": datetime.now().isoformat(timespec="seconds"),
    }

    # Proposed numbers for next quarter (written only if the analyst approves, in the app)
    result["revisions"] = propose_revisions(result)

    # Step 6 - Draft
    result["note"] = build_note(result)
    if save:
        save_run(result)
    return result


def run_on_filing(ticker: str, filing_date: str | None = None) -> dict:
    """Step 1 (fetch from the SEC), then the rest. Uses the newest release unless a date is given."""
    cik, _ = ticker_to_cik(ticker)
    filings = list_earnings_filings(cik)
    if filing_date:
        filings = [f for f in filings if f["filing_date"] == filing_date]
    if not filings:
        from agent.config import SetupError
        raise SetupError(f"No earnings release found for {ticker.upper()}" + (f" on {filing_date}." if filing_date else "."))
    release = download_press_release(ticker, cik, filings[0])
    return run_on_text(ticker, filings[0]["filing_date"], html_to_text(release["html"]), release["url"])
