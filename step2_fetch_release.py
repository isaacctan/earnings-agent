"""STEP 2 - Download a company's latest earnings press release from the SEC.

Run it from the VS Code terminal with:   python step2_fetch_release.py AAPL
(Swap AAPL for any ticker.)
"""

import sys

from agent.config import SetupError
from agent.parse import html_to_text
from agent.sec_client import download_press_release, list_earnings_filings, ticker_to_cik


def main() -> None:
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

    try:
        print(f"Looking up {ticker.upper()} at the SEC...")
        cik, name = ticker_to_cik(ticker)
        print(f"  Found: {name} (SEC ID {cik})")

        filings = list_earnings_filings(cik)
        if not filings:
            print("  No recent earnings announcements found for this company.")
            return
        print(f"  Found {len(filings)} recent earnings announcements:")
        for filing in filings:
            print(f"    - filed {filing['filing_date']}")

        latest = filings[0]
        print(f"\nDownloading the press release filed {latest['filing_date']}...")
        release = download_press_release(ticker, cik, latest)
    except SetupError as error:
        print(f"\nSomething needs fixing:\n  {error}")
        return

    text = html_to_text(release["html"])
    text_path = release["saved_path"].with_suffix(".txt")
    text_path.write_text(text, encoding="utf-8")

    print(f"  Source:  {release['url']}")
    print(f"  Saved:   {text_path}")
    print(f"  Length:  {len(text):,} characters")
    print("\n----- First 40 lines -----")
    print("\n".join(text.splitlines()[:40]))
    print("--------------------------")
    print("\nCheck: does this look like an earnings press release? If it looks like")
    print("the wrong document, note the ticker and date - that's your first failure-log entry.")
    print(f"\nNext, run:   python step3_run_agent.py {ticker.upper()}")


if __name__ == "__main__":
    main()
