---
name: add-company
description: Add a company to the agent's coverage list. Use when the team wants to cover a new ticker, swap a company, or set up estimates for one.
---

# Add a company to coverage

Goal: the company appears in the app, its earnings releases download correctly, and it has
estimate rows ready to fill in.

## Steps

1. **Confirm the ticker.** Ask for it if not given. Read `companies.csv` and stop if it is already listed.
2. **Add it to `companies.csv`** with its name and a short note (why it's covered). Keep the header and existing rows.
3. **Fetch its latest release.** Explain that this downloads from the SEC and is free, then run:
   `python step2_fetch_release.py TICKER`
4. **Check the right document came back.** Read the first 40 lines it prints. An earnings press
   release has a headline like "... Reports/Announces ... Quarter ... Results". If it looks like
   something else (an investor presentation, a cover page, a short notice):
   - tell the user plainly,
   - log it with `/log-failure` (it is failure F-002 if the cause is the exhibit picker),
   - do not change `pick_press_release` without showing the user the file names involved and
     adding a test for the new case in `tests/test_basics.py`.
5. **Check the metrics fit.** Skim the saved text in `data/releases/` for the four metrics in
   `agent/schemas.py`. If the company doesn't report one (for example, a bank has no
   operating income line), say so. Changing `METRICS` affects every company, so raise it
   as a team decision; don't change it yourself.
6. **Set up estimates.** Offer to pull consensus with `/pull-consensus` (free). That seeds EPS and
   revenue. For the other metrics, append rows to `estimates.csv` with the `estimate` column left for
   the team to fill in, and remind them: dollar amounts in millions, EPS in dollars, and write the
   method in the last column. Never invent an estimate.
7. **Summarize** what was added and what the team still has to do (fill in estimates, build the
   answer key with `/build-answer-key`).

## Don't

- Don't run `step3_run_agent.py` here; it costs money and the estimates aren't in yet.
- Don't remove the EXAMPLE rows from `estimates.csv` unless asked.
