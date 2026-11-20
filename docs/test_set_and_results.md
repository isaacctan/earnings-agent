# Test Set and Results

**Run date:** 2026-11-20

**Project version:** `7757470` (`main` after syncing the committed estimates)

**Live model:** Claude Haiku 5.5 for one fictional practice-release run

**Automated tests:** 40 passed with `pytest`; tests use `fake_claude` and do not call the live API.

## Pre-registered success criteria

The answer-key criteria were already defined in `eval/run_backtest.py`; they were not changed for this run:

1. Extraction accuracy is at least 95%.
2. No answer-key variance of 5% or more is missed.
3. Every `REVISE` call has verified supporting quotes.
4. No unverified figure is used in a call.

For the controlled cases below, the expected behavior is defined in the named test assertions. A case passes only when the observed behavior matches that expected behavior. These are deterministic software scenarios, not ten independent company releases.

## Controlled behavior cases

| # | Case and source test | Expected result | Actual result | Status |
|---|---|---|---|---|
| 1 | Clean fictional Q3 beat — `test_clean_beat_end_to_end` | Revenue verifies; R4 revises up; overall R9 is `REVISE UP` | Same; assertion passed | PASS |
| 2 | Invented EPS of 9.99 — `test_invented_number_is_stopped` | EPS fails verification; overall `NEEDS REVIEW` | Same; assertion passed | PASS |
| 3 | Driver quote absent from release — `test_invented_driver_quote_is_stopped` | Explanation fails quote check; overall `NEEDS REVIEW` | Same; assertion passed | PASS |
| 4 | Instruction embedded in release — `test_injected_instructions_force_review` | Suspicious text triggers R6 and `NEEDS REVIEW` | Same; assertion passed | PASS |
| 5 | Plausible but fabricated source sentence — `test_made_up_quote_fails` | Figure is unverified | `verified=False`; assertion passed | PASS |
| 6 | Number not present in the cited line — `test_number_must_be_inside_its_quote` | Figure is unverified | `verified=False`; assertion passed | PASS |
| 7 | Thousands mistakenly declared as millions — `test_scale_mix_up_is_caught` | Scale check rejects figure under R0 | Figure unverified; assertion passed | PASS |
| 8 | Estimate missing — `test_R1_no_estimate` | R1 returns `NEEDS REVIEW` | R1; assertion passed | PASS |
| 9 | Small positive variance inside 5% — `test_R2_small_variance_holds` | R2 returns `HOLD` | R2 `HOLD`; assertion passed | PASS |
| 10 | Large beat attributed to one-time item — `test_R3_one_time_holds` | R3 returns `HOLD` | R3 `HOLD`; assertion passed | PASS |
| 11 | Large recurring miss — `test_R4_recurring_revises_in_the_right_direction` | R4 returns `REVISE DOWN` | `REVISE DOWN`; assertion passed | PASS |
| 12 | Upward revenue call conflicts with downward EPS call — `test_R8_conflicting_signals` | R8 returns `NEEDS REVIEW` | R8; assertion passed | PASS |

**Controlled-case hit rate:** 12/12 expected behaviors matched (100%). This measures tested rule/validation scenarios, not extraction accuracy across releases.

## Answer-key backtest

The current answer key contains one fictional release and four labeled figures. We regenerated its saved result after discovering that the saved run was from an older version of the practice file.

| Scope | Correct figures | Checked | Extraction accuracy |
|---|---:|---:|---:|
| Example Devices Corp. fictional Q3 2026 release | 4 | 4 | 100% |

| Registered criterion | Result |
|---|---|
| Extraction accuracy >= 95% | PASS |
| No missed variances >= 5% | PASS |
| Every REVISE call is cited | PASS |
| No unverified figures used | PASS |

**Answer-key verdict:** PASS for this one fictional release. One release is not enough evidence to claim general accuracy.

## Failure reproduced verbatim

Before refreshing the stale saved result, the backtest printed:

```text
Figures checked: 4   Extraction accuracy: 75.0%

  [FAIL] 1. Extraction accuracy >= 95%
  [PASS] 2. No missed variances >= 5%
  [PASS] 3. Every REVISE call is cited
  [PASS] 4. No unverified figures used

Mismatches:
  - SAMPLE sample_release_FICTIONAL operating_income: agent None, answer key 18.922

Overall: the agent DOES NOT PASS (yet).
```

The saved result described the old Example Lending Corp. release, while the current practice file and answer key described Example Devices Corp. Re-running the current practice file corrected the mismatch. The backtest does not yet detect stale results when a file changes but keeps the same ticker/date key; see F-009 in [`failure_log.md`](./failure_log.md).

## What this does not establish

- Ten or more independently labeled real-company releases have **not** been evaluated.
- The 12 controlled cases use hand-scripted model responses, so they test checks and rules rather than real-model reliability.
- Live SEC fetching for the new coverage set and a live Yahoo Finance consensus pull remain to be checked.
- No shared API key is provided. Teammates use their own credentials; the automated tests require none.
