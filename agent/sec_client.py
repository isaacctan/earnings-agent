"""Talks to the SEC's free EDGAR website.

What this file can do:
  1. Turn a ticker (AAPL) into the SEC's ID number for that company (its "CIK").
  2. List the company's recent earnings announcements.
     (These are 8-K filings that include "Item 2.02 - Results of Operations".)
  3. Find and download the press release attached to one of them (Exhibit 99.1).
"""

import re
import time

import requests

from agent.config import RELEASES_DIR, SetupError, get_sec_user_agent

TICKER_LIST_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
FILING_FOLDER_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/"

# The SEC allows 10 requests per second. We pause between requests to stay far below.
PAUSE_SECONDS = 0.25


def _get(url: str) -> requests.Response:
    """Download one web address from the SEC, politely."""
    time.sleep(PAUSE_SECONDS)
    headers = {"User-Agent": get_sec_user_agent()}
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as error:
        raise SetupError(f"Could not reach the SEC website. Are you online? ({error})")
    if response.status_code == 403:
        raise SetupError(
            "The SEC refused the request (error 403). This usually means the "
            "SEC_USER_AGENT line in your .env file is missing a real name and email."
        )
    if response.status_code == 429:
        raise SetupError("The SEC says we are asking too fast. Wait a minute and retry.")
    response.raise_for_status()
    return response


def ticker_to_cik(ticker: str) -> tuple[int, str]:
    """Look up a ticker. Returns (CIK number, company name)."""
    ticker = ticker.strip().upper()
    companies = _get(TICKER_LIST_URL).json()
    for company in companies.values():
        if company["ticker"].upper() == ticker:
            return int(company["cik_str"]), company["title"]
    raise SetupError(f"The SEC has no company with the ticker '{ticker}'. Check the spelling.")


def list_earnings_filings(cik: int, limit: int = 8) -> list[dict]:
    """Return the company's most recent earnings announcements, newest first."""
    recent = _get(SUBMISSIONS_URL.format(cik=cik)).json()["filings"]["recent"]
    filings = []
    for form, items, accession, date, primary in zip(
        recent["form"],
        recent["items"],
        recent["accessionNumber"],
        recent["filingDate"],
        recent["primaryDocument"],
    ):
        if form == "8-K" and "2.02" in items:
            filings.append(
                {
                    "accession": accession,
                    "filing_date": date,
                    "primary_document": primary,
                }
            )
        if len(filings) >= limit:
            break
    return filings


def pick_press_release(file_names_and_sizes: list[tuple[str, int]], primary_document: str) -> str:
    """Choose which file in a filing is the earnings press release.

    Companies name their files differently, so this is a best guess:
      - first choice: a web page whose name looks like "ex99-1" / "ex991" / "exhibit99_1"
      - second choice: any web page with "ex99" in its name
      - fallback: the biggest web page that isn't the 8-K cover page
    """
    pages = [
        (name, size)
        for name, size in file_names_and_sizes
        if name.lower().endswith((".htm", ".html"))
        and name != primary_document
        and "index" not in name.lower()
    ]
    if not pages:
        return primary_document

    exhibit_99 = [p for p in pages if re.search(r"ex(hibit)?[-_]?99", p[0].lower())]
    for name, _ in sorted(exhibit_99):
        if re.search(r"99[-_.]?0?1(?!\d)", name.lower()):
            return name
    if exhibit_99:
        return sorted(exhibit_99)[0][0]

    return max(pages, key=lambda p: p[1])[0]


def find_press_release_url(cik: int, filing: dict) -> str:
    """Return the web address of the press release inside one filing."""
    folder = FILING_FOLDER_URL.format(cik=cik, accession=filing["accession"].replace("-", ""))
    listing = _get(folder + "index.json").json()["directory"]["item"]
    files = []
    for item in listing:
        size = item.get("size") or 0
        files.append((item["name"], int(size) if str(size).isdigit() else 0))
    return folder + pick_press_release(files, filing["primary_document"])


def download_press_release(ticker: str, cik: int, filing: dict) -> dict:
    """Download one press release and save it in data/releases/.

    Returns a small record: where it came from, where it was saved, and the raw page.
    """
    url = find_press_release_url(cik, filing)
    html = _get(url).text

    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = RELEASES_DIR / f"{ticker.upper()}_{filing['filing_date']}.html"
    saved_path.write_text(html, encoding="utf-8")

    return {"url": url, "saved_path": saved_path, "html": html}


def fiscal_year_end_month(cik: int) -> int:
    """The month the company's fiscal year ends (12 for December), as filed with the SEC."""
    value = str(_get(SUBMISSIONS_URL.format(cik=cik)).json().get("fiscalYearEnd") or "1231")
    return int(value[:2]) if value[:2].isdigit() and 1 <= int(value[:2]) <= 12 else 12
