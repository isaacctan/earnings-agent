# CLAUDE.md

This is the Earnings Revision Agent, a class project for an AI in Business course
(Product Management track: build an AI agent, then find where it breaks).
`docs/PROJECT_GUIDE.md` is the full specification. Read the relevant section before changing anything.

## Who you are working with

A three-person student team with finance knowledge and no programming background.

- Explain what a command does before asking anyone to run it.
- Keep code simple and commented in plain English. Prefer a few clear lines over a clever one.
- When something fails, say what went wrong and the one thing to do next.
- Don't add packages, frameworks, or files the project doesn't need.
- This is graded coursework. Help them understand what is built so they can explain it;
  don't hide how things work.

## The design principle (do not break this)

**Claude reads and judges. Code does the math and makes the call. A person approves.**

- The model never does arithmetic or unit conversion. That is `agent/numbers.py` and `agent/variance.py`.
- The model never decides. Calls come from the fixed rules in `agent/decide.py`.
- Every figure and every explanation carries a word-for-word source quote, checked by `agent/validate.py`.
  Anything unverified becomes NEEDS REVIEW. Never loosen a check to make a run "pass".
- All model calls go through `agent/llm.py` and return structured data defined in `agent/schemas.py`.
- The analyst note is built by `agent/draft.py` from verified facts. Do not have the model write it.
- Nothing is final without a human decision recorded through `agent/storage.py`.

## Map

| Path | Job |
|---|---|
| `agent/sec_client.py`, `agent/parse.py` | Step 1: fetch the release, turn it into text |
| `agent/extract.py`, `prompts/extract_v1.md` | Step 2: model copies out figures |
| `agent/numbers.py`, `agent/variance.py`, `agent/validate.py` | Step 3: convert, compare, check |
| `agent/classify.py`, `prompts/classify_v1.md` | Step 4: model explains variances, reads guidance |
| `agent/decide.py` | Step 5: rules R0-R9 |
| `agent/draft.py`, `agent/storage.py` | Step 6: note and logs |
| `agent/estimates.py` | Our book: reads and appends `estimates.csv` |
| `agent/consensus.py` | Pulls Yahoo Finance consensus into `data/consensus.csv`; seeds gaps in the book |
| `agent/revise.py` | Proposes next quarter's estimates; writes the ones an analyst approves |
| `agent/periods.py` | Fiscal year / quarter arithmetic |
| `agent/pipeline.py` | Runs steps 1-6 |
| `app.py` | Step 7: the review-and-approve screen (Streamlit) |
| `eval/` | Answer key and scoring |
| `samples/`, `redteam/` | Practice and attack files (fictional company only) |
| `docs/` | Guide, finance background, failure log, AI use log |

## Rules for changes

- Prompts are versioned files. To change one, copy it to the next version (`extract_v2.md`)
  and update `PROMPT_VERSION`; never edit a version that has results recorded against it.
- If you change a decision rule, update its test in `tests/test_agent.py` and the table in
  `docs/PROJECT_GUIDE.md` section 7 in the same change.
- Tests must never call the real API. Use the `fake_claude` fixture in `tests/conftest.py`.
- SEC requests go through `sec_client._get` (it sends the required header and rate-limits).
- `estimates.csv`, `data/consensus.csv`, `data/run_log.csv`, and `data/decisions.csv` are append-only.
- Consensus and our estimates are separate on purpose. `data/consensus.csv` records what the Street
  expected; `estimates.csv` is the team's book. Consensus may only fill gaps in the book
  (`seed_estimates`). Never overwrite or "refresh" a team estimate with consensus, and never change
  the book except through an approved revision or a number the team gives you.
- Never invent an estimate. If neither the team nor consensus has a number, leave it empty.
- Never read, print, or commit `.env`. Never put a key in code.
- Never edit `eval/labels.csv` to match the agent's output. The answer key is made by people, first.
- Test files must use the fictional SAMPLE company or real public filings. Don't invent
  figures for real companies.
- When you find a way the agent breaks, add it to `docs/failure_log.md` (use `/log-failure`).
- When you do substantial work, remind the team to add a line to `docs/ai_use_log.md`.

## Commands

| Task | Command |
|---|---|
| Check setup | `python step1_check_setup.py` |
| Fetch a release (free) | `python step2_fetch_release.py AAPL` |
| Run the agent on the practice file | `python step3_run_agent.py --sample` |
| Run the agent on a company | `python step3_run_agent.py AAPL` |
| Run the agent on any text file | `python step3_run_agent.py --file redteam/injection_FICTIONAL.txt --ticker SAMPLE` |
| Pull consensus and seed the book (free) | `python step4_pull_consensus.py AAPL` (or `--all`) |
| Open the app | `streamlit run app.py` |
| Run the code checks | `pytest` |
| Score against the answer key | `python eval/run_backtest.py` |

Running the agent calls the Claude API and costs a few cents per run. Ask before running
it across many releases.
