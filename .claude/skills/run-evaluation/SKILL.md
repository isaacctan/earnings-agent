---
name: run-evaluation
description: Score the agent against the answer key and summarize the results. Use when the team asks how accurate the agent is, wants backtest results, or needs numbers for the presentation.
---

# Run the evaluation

## Steps

1. Run `python eval/run_backtest.py` and read the output.
2. If it lists releases "in the answer key but not run yet":
   - tell the user how many, and that each run calls the Claude API and costs a few cents,
   - **ask before running them**,
   - then run each with `python step3_run_agent.py TICKER FILING_DATE`
     (or `--file PATH --ticker TICKER` for practice files) and re-run the backtest.
3. Report in plain English:
   - how many figures were checked and the extraction accuracy,
   - PASS or FAIL for each of the four tests, and the overall verdict,
   - every mismatch, with the agent's value beside the answer key's.
4. **Diagnose each mismatch** by reading the saved run in `data/runs/` and the release text.
   Classify the cause: wrong column, wrong line, scale error, GAAP vs adjusted, not found,
   or a labeling error. If you think the label is wrong, say so and let the team decide;
   never edit `eval/labels.csv` yourself.
5. For each distinct cause, check `docs/failure_log.md`. If it's new, add it with `/log-failure`.
   If it's an `anticipated` entry now seen for real, update its status to `observed`.
6. Offer a short results table the team can paste into slides: tests, pass/fail, the numbers.

## Rules

- Report failures as plainly as passes. The grade rewards knowing where it breaks.
- Don't change prompts, thresholds, checks, or rules to improve the score during this skill.
  If a change looks worthwhile, describe it and let the team choose. Any change means a new
  prompt version and a full re-run, so before/after results stay comparable.
- A score from only a few releases is not strong evidence. Say how many releases the numbers rest on.
