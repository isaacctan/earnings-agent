"""Checks Claude's work before anything is decided.

The rule: a number only counts if we can find it, word for word, in the release.
"""

import re

from agent.numbers import parse_printed_number
from agent.schemas import METRICS, ExtractedFigure

# Phrases that have no business being in an earnings release. If one shows up,
# someone may be trying to give the AI instructions through the document.
SUSPICIOUS_PHRASES = [
    "ignore previous", "ignore all", "ignore the above", "disregard", "system prompt",
    "you are now", "new instructions", "as an ai", "to the ai", "assistant:", "note to ai",
    "do not flag", "override",
]


def _squash(text: str) -> str:
    """Lower-case and remove spacing and table bars so small formatting differences don't matter."""
    return re.sub(r"[\s|]+", "", text.lower())


def quote_is_in_document(quote: str, document: str) -> bool:
    return bool(quote.strip()) and _squash(quote) in _squash(document)


def check_figure(figure: ExtractedFigure, document: str, estimate: float | None, actual: float | None) -> dict:
    """Return {"verified": True/False, "problems": [...], "warnings": [...]} for one figure."""
    problems, warnings = [], []

    if not figure.found:
        return {"verified": False, "problems": ["Not found in the release."], "warnings": []}

    if not quote_is_in_document(figure.source_quote, document):
        problems.append("The source quote does not appear in the release.")
    if _squash(figure.printed_value.replace("$", "")) not in _squash(figure.source_quote.replace("$", "")):
        problems.append("The number does not appear inside its own source quote.")
    if parse_printed_number(figure.printed_value) is None:
        problems.append(f"'{figure.printed_value}' could not be read as a number.")
    if METRICS[figure.metric]["unit"] == "USD per share" and figure.scale != "ones":
        problems.append("A per-share figure was given a scale other than 'ones'.")

    if estimate and actual is not None and not (0.2 <= abs(actual / estimate) <= 5):
        problems.append(
            "The reported figure is more than 5x away from the estimate. "
            "Likely a thousands/millions mix-up or the wrong line."
        )
    if figure.basis == "adjusted":
        warnings.append("This is an adjusted (non-GAAP) figure; the estimate may be on a GAAP basis.")
    if figure.basis == "unknown":
        warnings.append("Could not tell whether this figure is GAAP or adjusted.")

    return {"verified": not problems, "problems": problems, "warnings": warnings}


def find_suspicious_text(document: str) -> list[str]:
    """Return any suspicious phrases found in the release."""
    lowered = document.lower()
    return [phrase for phrase in SUSPICIOUS_PHRASES if phrase in lowered]
