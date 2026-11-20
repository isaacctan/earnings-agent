---
name: pull-consensus
description: Pull Wall Street consensus estimates from Yahoo Finance and seed the team's estimates with them. Use when setting up estimates for a company, refreshing consensus, or comparing the team's numbers with the Street.
---

# Pull consensus and seed the book

Background: `docs/PROJECT_GUIDE.md` section 6.1. In short, `data/consensus.csv` records what
the Street expected, and `estimates.csv` is the team's own book. Consensus only fills gaps in the
book. After that, the book changes only through revisions the team approves.

## Steps

1. Ask which company, or all of them. Explain that this downloads from Yahoo Finance and the SEC,
   is free, and does not need the Claude API key.
2. Run `python step4_pull_consensus.py TICKER` (or `--all`). If the user only wants a record of
   the Street's view, without touching `estimates.csv`, add `--no-seed`.
3. **Explain what came back** in a short table: quarter, metric, consensus, pre-report or forward,
   basis, number of analysts, and which rows were added to the book and which were skipped
   because the team already had a number.
4. **Check the quarters.** The first time a company is pulled, compare one forward EPS number with
   Yahoo Finance's website (the "Analysis" tab for that ticker) and confirm the quarter matches. If
   it is a quarter off, log it with `/log-failure` (it is F-007) and stop.
5. **Check the EPS basis.** If any EPS row says `adjusted`, explain that the agent extracts GAAP EPS,
   so a variance against this estimate may just be the difference between GAAP and adjusted. Suggest
   the team replace those rows with a GAAP number.
6. **Check the revenue definition.** Find the company's most recent release in `data/releases/`
   (fetch it with `step2_fetch_release.py` if it isn't there). Compare its "Total revenue" for the
   last reported quarter with the consensus for the next quarter. If they differ far more than the
   business could explain, the provider probably defines revenue differently (F-005). Say so, and
   let the team decide whether to replace the seeded revenue rows.
7. Remind the team that operating income and net income have no free consensus and still need
   their own estimates.

## Rules

- Never edit or delete rows in `data/consensus.csv` or `estimates.csv`. To correct an estimate,
  append a new row with the team's number and a method explaining why.
- Never replace a team estimate with consensus, even if asked to "refresh" the book. A refresh
  means pulling again (which records the new consensus), not overwriting the team's view. If the
  user really wants to adopt the new consensus for a metric, have them confirm, then append it as
  a team row with a method like "Adopted consensus of 2026-12-01 (team decision)".
- If Yahoo fails, don't look for another site to scrape. Suggest trying again later,
  `pip install --upgrade yfinance`, or entering numbers by hand.
