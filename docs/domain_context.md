# Finance background for this project

Reference for anyone (person or AI assistant) working on the agent. It covers how earnings are
published, where each figure sits in a release, and the traps that cause wrong extractions.

## How earnings reach the public

1. **Press release.** The company announces results in a press release, furnished to the SEC the
   same day as **Exhibit 99.1** to a **Form 8-K** under **Item 2.02**. It is unaudited and is the
   first source available. This is what the agent reads.
2. **Earnings call.** Usually the same or next day. Not used by the agent.
3. **10-Q (or 10-K for the fourth quarter).** The full report, typically days to weeks later.
   The fourth quarter has no 10-Q of its own; fourth-quarter figures are the 10-K full year
   minus the first nine months.

Some companies attach more than one exhibit to the 8-K (for example an investor presentation as
Exhibit 99.2), and file names are not standardized.

## Anatomy of a release

- **Headline and highlights.** A few bullet points, usually rounded and in words
  ("$165.5 million"). Often mixes GAAP and adjusted figures.
- **Management commentary.** Quotes explaining results. This is where drivers are found.
- **Outlook / guidance.** Expectations for future periods, when the company gives them.
- **Financial tables.** Income statement, balance sheet, sometimes segment and credit tables.
  More precise than the highlights, and each table states its scale ("in thousands").
- **Non-GAAP reconciliations.** Tables bridging GAAP figures to adjusted ones.

Prefer the tables for figures and the commentary for explanations.

## The four metrics

| Metric | Where to find it | Watch for |
|---|---|---|
| Total revenue | Income statement: "Total revenue", "Total net sales" (Apple), "Revenue" (Microsoft, NVIDIA), "Total revenues" (Alphabet) | Segment or product subtotals sit just above the total. |
| Operating income | Income statement: "Operating income" or "Income from operations" | Adjusted or non-GAAP operating income in highlights and reconciliations; segment operating income tables. |
| Net income | Income statement | Adjusted net income is not GAAP; "attributable to" lines when there are minority interests. |
| Diluted EPS | Bottom of the income statement, often under an "Earnings per share" heading as "Diluted" | Basic EPS is on the line above; adjusted EPS appears in highlights (NVIDIA leads with it). |

## Big-tech specifics

- **Fiscal years.** Apple's ends in late September, Microsoft's on June 30, NVIDIA's in late January,
  Amazon's and Alphabet's in December. Fiscal years are named by the year they end in, so NVIDIA's
  quarter ending October 2026 is its fiscal 2027 Q3.
- **52/53-week calendars.** Apple and NVIDIA end quarters on a Saturday or Sunday near month end,
  not on the last day of the month.
- **Year-to-date and trailing figures.** Amazon highlights trailing-twelve-month cash flow;
  Apple's fourth-quarter release shows full-year columns. Make sure a figure is the quarter's.
- **Non-GAAP emphasis.** NVIDIA leads with non-GAAP figures and consensus follows them.
- **Equity-investment gains.** Alphabet's and Amazon's net income can swing with gains or losses on
  investments that sit below operating income. These are usually one-time for estimate purposes.
- **Guidance styles.** Apple gives qualitative or ranged guidance on the call rather than in the
  release; Microsoft gives segment guidance on the call; NVIDIA and Amazon give revenue (and
  operating income, for Amazon) ranges in the release.

## Traps

- **Wrong column.** Tables show the current quarter beside the prior-year quarter, and often
  year-to-date columns. The current quarter is usually, but not always, the first column.
- **Scale.** Large companies usually report in millions; smaller ones in thousands. Highlights are
  often in billions. Per-share figures are never scaled.
- **Negatives.** Parentheses mean negative: (3.2) is -3.2.
- **GAAP versus adjusted.** Compare like with like. An estimate built on adjusted EPS should not
  be compared with GAAP EPS.
- **One-time items.** Gains or losses on sales, legal settlements, restructuring, storm-related
  reserves, tax items, debt-extinguishment costs, acquisition costs. These explain a variance
  without changing the outlook.
- **Restatements and reclassifications.** Prior-period figures may be revised, and the release may
  show both old and new.
- **Guidance forms.** Point estimates, ranges, qualitative statements, and partial updates
  (raising one metric while lowering another).

## What "revise" means here

An analyst revises estimates when new information changes the expected path of the business.
A surprise caused by the ongoing business (volume, yield, credit trends, costs) usually should
carry forward in part. A surprise caused by a one-time item usually should not. A change in
guidance is direct evidence about the future and often matters more than the quarter's results.

## Consensus estimates

**Consensus** is the average of the estimates published by the analysts who cover a company. A
"beat" or "miss" in the press means against consensus. Things to know:

- Consensus EPS is usually on the company's adjusted basis, not GAAP.
- Data providers each standardize line items their own way, so "revenue" in a consensus feed may
  not match the release's "Total revenue" line exactly.
- Small companies may have only a few analysts, so one outlier moves the average. Look at the low,
  the high, and the number of analysts, not just the average.
- Consensus moves after every release as analysts revise. The figure that matters for judging a
  release is the **pre-report** consensus, the last one before the company reported.

An analyst's own estimates often start near consensus and then diverge as they form their own view.
Where they diverge, and whether they turn out right, is the substance of an analyst's work.
