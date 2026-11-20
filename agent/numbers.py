"""Turns numbers as printed in a release into plain numbers in standard units.

Claude copies the number exactly as printed ("165,512") and says what scale the
table is in ("thousands"). This file does the conversion, so the AI never does math.
"""

import re

from agent.schemas import METRICS

_TO_MILLIONS = {"ones": 1 / 1_000_000, "thousands": 1 / 1_000, "millions": 1, "billions": 1_000}


def parse_printed_number(text: str) -> float | None:
    """'165,512' -> 165512.0   '(3.2)' -> -3.2   '$1.25' -> 1.25   '—' -> None"""
    cleaned = text.strip().replace("$", "").replace(",", "").replace(" ", "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    if cleaned.startswith("-") or cleaned.startswith("−"):
        negative = True
        cleaned = cleaned[1:]
    if not re.fullmatch(r"\d+(\.\d+)?", cleaned):
        return None
    value = float(cleaned)
    return -value if negative else value


def to_standard_unit(metric: str, printed_value: str, scale: str) -> float | None:
    """Convert a printed number to the unit we store for that metric."""
    value = parse_printed_number(printed_value)
    if value is None:
        return None
    if METRICS[metric]["unit"] == "USD millions":
        return round(value * _TO_MILLIONS[scale], 4)
    return value  # per-share figures are stored as printed
