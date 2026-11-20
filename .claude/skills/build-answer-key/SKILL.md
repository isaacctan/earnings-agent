---
name: build-answer-key
description: Help a team member hand-label the true figures for an earnings release in eval/labels.csv. Use when building or extending the answer key for the backtest.
---

# Build the answer key for one release

The answer key is only worth something if people make it without seeing the agent's answer.
Your job is to make labeling fast and consistent. It is not to do the labeling.

## Hard rules

- **Never fill in `true_value` yourself**, never suggest a value, and never confirm or deny a
  value the user proposes. The human reads the release and decides.
- **Never open `data/runs/`** during this skill. If a run already exists for this release, tell
  the user the label will be less independent and ask whether to continue.
- Never change an existing label without the user telling you the new value and why.

## Steps

1. Ask which ticker and release (filing date, or file name for a practice file), and who is labeling.
2. Make sure the release text is on disk in `data/releases/TICKER_DATE.txt`. If it isn't, run
   `python step2_fetch_release.py TICKER` (free) and explain what it does.
3. Tell the user to open that `.txt` file in VS Code. Give them the labeling rules:
   - the **current quarter** column, not the prior year and not year-to-date
   - **GAAP** figures
   - dollar amounts converted to **millions** (a table in thousands showing 165,512 is 165.512)
   - EPS in dollars as printed
   - if the release doesn't report the metric, leave the value blank
   - when unsure between two lines, write down both and flag it for the team
4. Go through the metrics in `agent/schemas.py` one at a time. For each, state the definition
   and ask for the value. You may help with *where to look* in general terms (see
   `docs/domain_context.md`), not with what the number is.
5. Append the rows to `eval/labels.csv`: `ticker, release_date, metric, true_value, unit, labeled_by`.
   `release_date` must be the filing date (or the file name without `.txt`), matching how runs are saved.
6. Ask whether any figure was hard to find or ambiguous. Hard cases are worth noting in
   `docs/failure_log.md` as things likely to trip the agent.
7. Remind them of the team process: two people label independently, a third resolves differences.

## Also worth labeling (optional, in a separate sheet)

For each large variance: is the driver recurring or one-time, in the labeler's judgment? The
scoring script doesn't use this, but the team needs it to report driver-classification accuracy.
