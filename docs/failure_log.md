# Failure log

Every way the agent has broken or could break. This file is the raw material for the
"where it breaks" part of the presentation. Add an entry the moment you find something;
don't wait until it is fixed.

**Status values:** `anticipated` (expected from the design, not yet seen) · `observed` (seen in a real run)
· `mitigated` (a check or rule now handles it) · `accepted` (documented, not fixed).

**Severity:** `high` = a wrong number or call could reach the analyst looking correct ·
`medium` = wrong or missing, but flagged for review · `low` = inconvenience.

## Entry template

```
### F-000  Short title
- Date found:
- Found by:
- Release / file:
- What happened:
- What should have happened:
- Why (root cause):
- Severity:
- Status:
- What we did about it:
```

---

## Entries

### F-001  A verified figure can be from the wrong column
- Date found: 2026-11-16
- Found by: design review
- Release / file: any release with prior-period columns
- What happened: (anticipated) the model could return the prior-year figure with a valid quote; every check passes because the number is on the quoted line.
- What should have happened: the current-quarter figure.
- Why (root cause): checks confirm a number exists in the release, not which period it belongs to.
- Severity: high
- Status: anticipated
- What we did about it: only the answer key catches it. Measure how often it happens in the backtest.

### F-002  The press-release picker can choose the wrong exhibit
- Date found: 2026-11-16
- Found by: design review
- Release / file: filings with unusual file names or several exhibits
- What happened: (anticipated) a different exhibit, such as an investor presentation, is downloaded.
- What should have happened: Exhibit 99.1.
- Why (root cause): selection relies on file names, which companies don't standardize.
- Severity: medium
- Status: anticipated
- What we did about it: record each ticker and date where it happens.

### F-003  The injection scan only knows a fixed list of phrases
- Date found: 2026-11-16
- Found by: design review
- Release / file: redteam/
- What happened: (anticipated) an instruction worded to avoid the listed phrases is not flagged by the scan.
- What should have happened: NEEDS REVIEW via rule R6.
- Why (root cause): keyword matching.
- Severity: medium
- Status: anticipated
- What we did about it: the quote checks and fixed rules still apply. Test with reworded attacks.

### F-004  Driver classification is not independently verified
- Date found: 2026-11-16
- Found by: design review
- Release / file: any
- What happened: (anticipated) the model labels a one-time item as recurring, citing a real sentence that doesn't actually support that.
- What should have happened: one-time, or unclear.
- Why (root cause): code can confirm a quote exists, not what it means.
- Severity: high
- Status: anticipated
- What we did about it: hand-label drivers in the backtest and report the agreement rate.

### F-005  Provider revenue may be defined differently from the release
- Date found: 2026-11-19
- Found by: design review
- Release / file: any company with seeded revenue
- What happened: (anticipated) Yahoo's revenue consensus may use a different definition from the release's own revenue total.
- What should have happened: like-for-like comparison.
- Why (root cause): data providers standardize line items their own way.
- Severity: high (a definitional gap looks like a large beat or miss, and could produce a REVISE call)
- Status: anticipated
- What we did about it: every run using a seeded revenue estimate is flagged; `/pull-consensus` checks the definition against a real release.

### F-006  Consensus EPS may be adjusted while the agent extracts GAAP
- Date found: 2026-11-19
- Found by: design review
- Release / file: companies that report adjusted EPS
- What happened: (anticipated) Yahoo has no GAAP consensus for the company, so the adjusted figure is used.
- What should have happened: GAAP versus GAAP.
- Why (root cause): Street consensus is usually built on the adjusted figure companies emphasize.
- Severity: medium
- Status: mitigated
- What we did about it: GAAP consensus is requested first; any adjusted seed is labelled in capitals and flagged on every run that uses it.

### F-007  Forward consensus could be placed in the wrong fiscal quarter
- Date found: 2026-11-19
- Found by: design review
- Release / file: companies with unusual fiscal calendars
- What happened: (anticipated) Yahoo labels forward periods only "current" and "next" quarter; the code infers which fiscal quarter that is.
- What should have happened: the correct fiscal quarter.
- Why (root cause): inference from the last reported quarter plus the SEC fiscal year end.
- Severity: high (estimates compared against the wrong quarter's results)
- Status: anticipated
- What we did about it: no forward rows are saved if the last reported quarter can't be found; check the first pull for each company against Yahoo's website.

### F-008  Free consensus is unofficial and can stop working
- Date found: 2026-11-19
- Found by: design review
- Release / file: n/a
- What happened: (anticipated) `yfinance` reads Yahoo's website, which can change without notice.
- What should have happened: n/a
- Why (root cause): no free, licensed consensus feed.
- Severity: low (the agent still runs on hand-entered estimates)
- Status: accepted
- What we did about it: consensus is optional; failures give a plain message; nothing else depends on it.
