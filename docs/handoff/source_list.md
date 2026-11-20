# Source List

**Updated:** 2026-11-20

## Data and reference sources

| Source | Used for | Link / project location | Notes |
|---|---|---|---|
| U.S. SEC EDGAR company ticker list | Resolve ticker to CIK | [SEC company tickers JSON](https://www.sec.gov/files/company_tickers.json); `agent/sec_client.py` | SEC source; requests include the configured contact name/email. |
| SEC company submissions and filing archives | Find earnings 8-Ks, fiscal year-end data, and press-release exhibits | [SEC EDGAR](https://www.sec.gov/edgar/search/); `agent/sec_client.py` | The program downloads a candidate earnings exhibit; the analyst should confirm it is the intended release. |
| SEC company filings for current coverage | Public filings for AAPL, MSFT, NVDA, AMZN, and GOOGL | [AAPL](https://www.sec.gov/edgar/browse/?CIK=320193), [MSFT](https://www.sec.gov/edgar/browse/?CIK=789019), [NVDA](https://www.sec.gov/edgar/browse/?CIK=1045810), [AMZN](https://www.sec.gov/edgar/browse/?CIK=1018724), [GOOGL](https://www.sec.gov/edgar/browse/?CIK=1652044) | Filing values used for a particular decision should be cited to its exact release or filing, not just this index page. |
| Yahoo Finance | Optional consensus estimates | [Yahoo Finance](https://finance.yahoo.com/); `agent/consensus.py`, `data/consensus.csv` | Retrieved through `yfinance`. Unofficial and subject to availability, definition, and licensing limitations described in `docs/PROJECT_GUIDE.md`. |
| yfinance | Python interface used to retrieve Yahoo Finance consensus | [yfinance documentation](https://ranaroussi.github.io/yfinance/) | A community package; it is not an official Yahoo Finance API. |
| Anthropic Claude API | Language-model extraction and classification | [Claude models overview](https://platform.claude.com/docs/en/models/overview), `agent/llm.py` | Model calls require each user's own API key and may incur charges. |
| Fictional Example Devices practice release | No-cost-safe example input for tests and practice | [`samples/sample_release_FICTIONAL.txt`](../../samples/sample_release_FICTIONAL.txt) | Entirely fictional figures; not a source for real-company estimates. |

## Team estimate source audit

The committed rows in [`estimates.csv`](../../estimates.csv) describe their formulas in the `method` column. Examples include historical revenue multiplied by an assumed growth rate, a guidance midpoint, and estimates derived from assumed margins, taxes, and share counts.

**Citation gap:** the estimate rows do not include direct URLs or filing dates for the underlying historical figures or guidance. This source list therefore records the methods but does not independently validate the estimates. Before presenting them as sourced estimates, the team should add a companion citation for each key assumption (company, fiscal period, metric, source URL, page/table or quote, and date accessed). Do not treat the values as independently verified by this document.
