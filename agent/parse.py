"""Turns a downloaded press release (a web page) into plain readable text.

Tables are kept, one row per line, with " | " between the cells, because the
numbers we care about live in tables.
"""

import re

from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Throw away code and styling that isn't part of the document.
    for tag in soup(["script", "style", "head"]):
        tag.decompose()

    # Rewrite each table as simple lines of text.
    for table in soup.find_all("table"):
        lines = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            cells = [c for c in cells if c]  # drop empty spacer cells
            if cells:
                lines.append(" | ".join(cells))
        table.replace_with("\n" + "\n".join(lines) + "\n")

    text = soup.get_text("\n")

    # Tidy up: odd spaces, trailing spaces, and big gaps of blank lines.
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
