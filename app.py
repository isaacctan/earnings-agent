"""The visual app: fetch a release, run the agent, review its recommendation, record your decision.

Run it from the VS Code terminal with:   streamlit run app.py
It opens in your web browser. Press Ctrl+C in the terminal to stop it.
"""

import pandas as pd
import streamlit as st

from agent.config import PROJECT_DIR, SetupError
from agent.consensus import pull_consensus, save_consensus, seed_estimates
from agent.parse import html_to_text
from agent.pipeline import run_on_text
from agent.schemas import METRICS
from agent.sec_client import download_press_release, list_earnings_filings, ticker_to_cik
from agent.revise import apply_revisions
from agent.storage import record_decision

st.set_page_config(page_title="Earnings Revision Agent", layout="wide")
st.title("Earnings Revision Agent")
st.caption("Reads an earnings release, compares it with our estimates, and recommends: revise up, revise down, hold, or needs review.")

companies = pd.read_csv(PROJECT_DIR / "companies.csv")
state = st.session_state  # the app's memory between clicks (Streamlit re-runs this file on every click)


def set_release(ticker: str, date: str, source: str, text: str) -> None:
    state["release"] = {"ticker": ticker, "date": date, "source": source, "text": text}
    state.pop("result", None)


# ---- Sidebar: choose where the release comes from -----------------------------
with st.sidebar:
    st.header("1. Choose a release")
    mode = st.radio("Source", ["From the SEC", "Practice / red-team file"])

    if mode == "From the SEC":
        ticker = st.selectbox(
            "Company",
            companies["ticker"],
            format_func=lambda t: f"{t} - {companies.set_index('ticker').loc[t, 'name']}",
        )
        if st.button("Find earnings releases", type="primary"):
            try:
                with st.spinner("Asking the SEC..."):
                    cik, name = ticker_to_cik(ticker)
                    state["company"] = {"ticker": ticker, "cik": cik, "name": name,
                                        "filings": list_earnings_filings(cik)}
            except SetupError as error:
                st.error(str(error))

        company = state.get("company")
        if company and company["ticker"] == ticker and company["filings"]:
            dates = [filing["filing_date"] for filing in company["filings"]]
            chosen_date = st.selectbox("Release (by date filed)", dates)
            if st.button("Download this release"):
                try:
                    with st.spinner("Downloading from the SEC..."):
                        filing = company["filings"][dates.index(chosen_date)]
                        release = download_press_release(ticker, company["cik"], filing)
                        set_release(ticker, chosen_date, release["url"], html_to_text(release["html"]))
                except SetupError as error:
                    st.error(str(error))
        elif company and company["ticker"] == ticker:
            st.warning("No recent earnings announcements found.")
        st.caption("To change the company list, edit companies.csv.")

        st.divider()
        st.markdown("**Consensus estimates**")
        if st.button("Pull consensus from Yahoo Finance"):
            try:
                with st.spinner("Asking Yahoo Finance..."):
                    pulled = pull_consensus(ticker)
                    save_consensus(pulled)
                    seeded = seed_estimates(pulled)
                st.success(f"Saved {len(pulled)} consensus figures. Added {len(seeded)} new rows to estimates.csv "
                           "where we had no estimate; existing estimates were left alone.")
            except SetupError as error:
                st.error(str(error))
        st.caption("EPS and revenue only. Our own estimates are never overwritten.")

    else:
        files = sorted((PROJECT_DIR / "samples").glob("*.txt")) + sorted((PROJECT_DIR / "redteam").glob("*.txt"))
        chosen_file = st.selectbox("File", files, format_func=lambda p: f"{p.parent.name}/{p.name}")
        file_ticker = st.text_input("Ticker to compare estimates against", "SAMPLE")
        if st.button("Load this file", type="primary"):
            set_release(file_ticker.upper(), chosen_file.stem, str(chosen_file), chosen_file.read_text(encoding="utf-8"))
        st.caption("Practice files use a made-up company. Drop your own .txt files into redteam/ to test them.")

release = state.get("release")
if not release:
    st.info("Choose a release on the left to begin. New here? Try **Practice / red-team file** first.")
    st.stop()

# ---- Main area ----------------------------------------------------------------
st.subheader(f"{release['ticker']} - release '{release['date']}'")
tab_agent, tab_release = st.tabs(["Agent recommendation", "The press release"])

with tab_release:
    st.caption(f"Source: {release['source']} · {len(release['text']):,} characters")
    st.text_area("Release text", release["text"], height=550, label_visibility="collapsed")

with tab_agent:
    st.markdown("**2. Run the agent**")
    if st.button("Run the agent on this release", type="primary"):
        try:
            with st.spinner("Claude is reading the release (about 20-60 seconds)..."):
                state["result"] = run_on_text(release["ticker"], release["date"], release["text"], release["source"])
        except SetupError as error:
            st.error(str(error))
        except Exception as error:  # show any other problem instead of crashing the page
            st.error(f"The run failed: {error}")

    result = state.get("result")
    if not result:
        st.caption("Uses your Claude API key. Each run costs a few cents.")
        st.stop()

    overall = result["overall"]
    left, middle, right = st.columns(3)
    left.metric("Recommendation", overall["call"])
    middle.metric("Confidence", overall["confidence"].title())
    right.metric("Period", f"Q{result['fiscal_quarter']} {result['fiscal_year']}")
    st.write(f"{overall['reason']} *(rule {overall['rule']})*")

    if result["flags"]:
        st.warning("**Check before approving**\n\n" + "\n".join(f"- {flag}" for flag in result["flags"]))

    table = pd.DataFrame([
        {
            "Metric": METRICS[row["metric"]]["label"],
            "Our estimate": row["estimate"],
            "Consensus": row.get("consensus"),
            "Reported": row["actual"],
            "vs. ours %": row["pct"],
            "vs. consensus %": row.get("consensus_pct"),
            "Verified": "yes" if row["verified"] else "NO",
            "Driver": row["driver_kind"].replace("_", "-"),
            "Call": row["call"],
            "Rule": row["rule"],
            "Suggested change %": row["suggested_change_pct"],
        }
        for row in result["metrics"]
    ])
    st.dataframe(table, hide_index=True)

    with st.expander("Evidence: the exact lines each number and explanation came from"):
        for row in result["metrics"]:
            if row["source_quote"]:
                st.markdown(f"**{METRICS[row['metric']]['label']}** - printed as `{row['printed_value']}` ({row['scale']})")
                st.code(row["source_quote"], language=None)
            if row["driver_quote"]:
                st.markdown(f"*Why:* {row['driver_explanation']}")
                st.code(row["driver_quote"], language=None)
        if result["guidance"]["source_quote"]:
            st.markdown(f"**Guidance ({result['guidance']['status']})** - {result['guidance']['summary']}")
            st.code(result["guidance"]["source_quote"], language=None)

    with st.expander("The draft analyst note"):
        st.markdown(result["note"])

    st.divider()
    st.markdown("**3. Your decision** - nothing is final until a person signs off.")

    revisions = [r for r in result.get("revisions", []) if r["base"] is not None]
    final_values = {}
    if revisions:
        st.caption(
            f"Our estimates for Q{revisions[0]['quarter']} {revisions[0]['fiscal_year']}. Each box starts at the "
            "agent's proposal. Change any number before approving; approved numbers are added to our estimates."
        )
        for r in revisions:
            unit = METRICS[r["metric"]]["unit"]
            step, fmt = (0.01, "%.2f") if unit == "USD per share" else (0.1, "%.1f")
            change = f"{r['change_pct']:+.1f}%" if r["change_pct"] is not None else "no change"
            source = "ours" if r["base_source"] == "our estimate" else "consensus"
            name, current, proposal = st.columns([2, 2, 2])
            name.markdown(f"**{METRICS[r['metric']]['label']}**")
            current.caption(f"Current: {r['base']:,.2f} ({source}) · Agent: {change}")
            final_values[r["metric"]] = proposal.number_input(
                METRICS[r["metric"]]["label"], value=float(r["proposed"]), step=step, format=fmt,
                key=f"rev_{result['run_at']}_{r['metric']}", label_visibility="collapsed",
            )
    else:
        st.caption("No estimates or consensus on file for next quarter, so there is nothing to revise yet. "
                   "Pull consensus or add estimates for next quarter to estimates.csv.")

    edited = any(abs(final_values[r["metric"]] - r["proposed"]) > 1e-9 for r in revisions)
    choice = st.radio("Decision", ["Approve", "Reject"], horizontal=True)
    action = "Reject" if choice == "Reject" else ("Approve with edits" if edited else "Approve")
    comment = st.text_input("Comment (required for edits and rejections)")
    if st.button(f"Save: {action}"):
        if action != "Approve" and not comment.strip():
            st.error("Add a comment explaining the edit or rejection.")
        else:
            record_decision(result, action, comment.strip())
            written = apply_revisions(result, final_values, action) if action != "Reject" else []
            where = "samples/sample_estimates.csv" if result["ticker"] == "SAMPLE" else "estimates.csv"
            st.success(f"Decision saved to data/decisions.csv. {len(written)} estimate(s) added to {where}.")
