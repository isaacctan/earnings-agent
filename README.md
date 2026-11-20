# Earnings Revision Agent

A class project that helps an analyst review quarterly earnings and decide whether their estimates may need to change. It supports the first pass of analysis; it does not make investment recommendations, and a person must approve any proposed estimate changes.

## What it does

For a selected earnings release, the agent:

1. Gets the release from the SEC or loads a practice file.
2. Uses Claude to extract revenue, operating income, net income, and diluted EPS, with quotes from the release.
3. Uses Python to check the quotes, convert units, and compare reported figures with the team's estimates.
4. Uses Claude to explain large differences and read management's guidance.
5. Applies fixed rules to recommend **REVISE UP**, **REVISE DOWN**, **HOLD**, or **NEEDS REVIEW**.
6. Drafts an analyst note from the verified results.
7. Waits for an analyst to approve, edit, or reject proposed next-quarter estimates.

> **Claude reads and judges. Code does the math and makes the call. A person approves.**

The current coverage list is in [`companies.csv`](./companies.csv). Wall Street consensus is stored separately from the team's estimates; it can help fill missing estimates, but it does not overwrite the team's book.

## Get started

New to Python? Follow [`START_HERE.md`](./START_HERE.md) for a step-by-step setup walkthrough. [`docs/PROJECT_GUIDE.md`](./docs/PROJECT_GUIDE.md) explains the system and its decision rules in detail.

Quick start in a terminal from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and add your SEC name/email and your own Anthropic API key. Keep this file private: `.env` is excluded by `.gitignore`. Each teammate should use their own API key. The agent's live Claude calls incur usage charges.

Then check the setup and run the practice file:

```bash
python step1_check_setup.py
python step3_run_agent.py --sample
```

To open the review app:

```bash
streamlit run app.py
```

The app opens in a browser. Choose **Practice / red-team file** to try a sample, or **From the SEC** to select a covered company and release.

## Other useful commands

```bash
python step2_fetch_release.py AAPL       # Download an SEC release
python step4_pull_consensus.py AAPL      # Pull consensus and fill estimate gaps
pytest                                   # Run automated tests; tests do not call the live API
python eval/run_backtest.py              # Score saved runs against the answer key
```

Run the live agent only when you are ready to use API credits. Start with one practice run; ask the team before running many releases.

## Where things live

| Path | Purpose |
|---|---|
| `agent/` | Fetching, extraction, calculation, verification, rules, and estimate handling |
| `prompts/` | Versioned instructions sent to Claude |
| `app.py` | Analyst review and approval screen |
| `estimates.csv` | The team's estimate book |
| `data/consensus.csv` | Wall Street consensus history |
| `eval/` | Human-made answer key and evaluation script |
| `samples/`, `redteam/` | Fictional practice and adversarial test releases |
| `docs/` | Project guide, finance context, and project logs |
| `tests/` | Automated checks |

If a figure or explanation cannot be verified against the release, the agent should flag it for review rather than silently treating it as correct. Its recommendation is a draft, not a substitute for analyst judgment.
