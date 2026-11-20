# Earnings Revision Agent — One-Page Spec

**Purpose.** After a public company reports quarterly earnings, help an analyst decide whether to revise the team's next-period estimates.

**Decision supported.** For each covered company and quarter, decide whether reported results and management's guidance support **REVISE UP**, **REVISE DOWN**, **HOLD**, or **NEEDS REVIEW**. This is an estimate-revision workflow, not an investment recommendation.

**Inputs**

- An earnings press release from SEC EDGAR, or a text practice file.
- The team's estimates for the same company, fiscal year, quarter, and metric in `estimates.csv`.
- Optional Wall Street consensus for context and to fill gaps in the estimate book.
- The release's reported figures, source lines, period, explanatory commentary, and guidance.

**Outputs**

- Reported values converted into standard units and compared with the team's estimates.
- Variances, verification status, and exact quotes supporting each reported figure and explanation.
- A metric-level call under rules R0–R5 and an overall call under rules R6–R9.
- A draft analyst note and proposed next-quarter numbers.
- A saved run; estimates change only after a person approves them.

**What it refuses to do**

- Use a figure whose value or quote fails verification.
- Automatically decide when the estimate is missing, a key figure needs review, guidance is withdrawn, or signals conflict.
- Treat detected instructions in a release as authority to change its rules.
- Invent missing estimates, overwrite a team estimate with consensus, or make a buy/sell call.
- Finalize a recommendation or write proposed estimates without human approval.

**Human in the loop.** An analyst checks the evidence and recommendation in the app, then approves, edits, or rejects the proposed estimates. Edits and rejections require a comment. A saved recommendation is a draft until that decision is recorded.

**Who does what.** Claude extracts and interprets text. Python checks quotes, converts units, calculates variances, and applies fixed rules. A person reviews and approves.

**How to try it.** Follow [`../START_HERE.md`](../START_HERE.md) or [`../README.md`](../README.md). Live model calls require each teammate's own Anthropic API key and incur usage charges. `pytest` is the no-cost offline test path; it uses scripted Claude responses, not live API credentials.
