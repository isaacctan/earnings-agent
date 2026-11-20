# Status Memo — Earnings Revision Agent

**Date:** 2026-11-20

**Repository:** [isaacctan/earnings-agent](https://github.com/isaacctan/earnings-agent) (private)

## Current status

The repository is runnable from its beginner instructions. It contains a fictional practice workflow, a Streamlit review screen, automated tests, and an evaluation script. The owner has committed estimate rows for AAPL, MSFT, GOOGL, AMZN, and NVDA; the local checkout was synced to those commits. Each teammate still needs their own Anthropic API key and SEC name/email in a private `.env`. No shared credentials are supplied. Offline automated tests use a scripted model and require no key.

## What changed since the proposal, and why

- Coverage shifted from consumer lenders to five large-cap technology companies. Metrics are now revenue, operating income, net income, and diluted EPS.
- The project added separate consensus tracking and analyst-approved next-quarter estimate proposals, keeping the team's estimates distinct from Wall Street consensus.
- The owner added rough model estimates for the five covered companies. Their method descriptions are in `estimates.csv`; direct source URLs for the assumptions are not yet recorded.
- A beginner-oriented README and handoff documents now explain the workflow and controls.

## What broke

The first current answer-key run reported 75% extraction accuracy because it compared the updated Example Devices answer key with an older saved result for the former Example Lending practice file. Verbatim mismatch:

```text
SAMPLE sample_release_FICTIONAL operating_income: agent None, answer key 18.922
```

We reran the current fictional sample once; it matched all four labels. The test runner still keys saved runs by ticker/date rather than source contents, so stale saved results can recur after a practice file changes. This is recorded as F-009.

## Evidence and known weaknesses

- Current answer-key result: 4/4 figures correct (100%); all four registered backtest criteria pass. Evidence is one fictional release only.
- Controlled offline behavior suite: 12/12 selected scenarios matched their expected outcomes; full suite: 40 tests passed.
- Claude's recurring/one-time judgment cannot be verified semantically by code. A quote can be real but not support the explanation.
- Filing exhibit selection and prompt-injection detection have known limitations (F-002 and F-003).
- Yahoo Finance consensus is unofficial; revenue definitions and fiscal-quarter mapping can be wrong.
- Team estimate methods are described, but exact public-source links are missing.
- Live SEC and Yahoo flows for the new technology-company coverage, and a multi-release live Claude evaluation, are not established by this one-sample run.

## What remains / what we need

1. Build a human-labeled set of at least ten earnings releases before claiming broad accuracy. The team must label true figures before running the agent on those cases.
2. Add the source filing or investor-relations URL and date behind each estimate assumption.
3. Have the repository owner invite the paired team on GitHub and confirm they can clone it. Do not share API keys; each person configures their own `.env`.
4. Run and manually verify a live SEC download and Yahoo consensus pull for the current coverage list.
5. Add a safeguard that warns when a saved run may not match the current release file.

**Need from the owner:** teammate GitHub usernames for repository access; the source links behind the committed estimate formulas; and agreement on which ten releases to label. Running a broad live-model evaluation should wait until the answer key is ready and the team agrees to the API cost.
