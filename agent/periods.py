"""Fiscal periods: which fiscal year and quarter a date belongs to.

Many companies' fiscal year ends in December, but not all. Apple's ends in September, so
the quarter ending in December 2026 is its fiscal 2027 Q1; NVIDIA's ends in January. The month a
company's fiscal year ends comes from the SEC.
"""

from datetime import date

import pandas as pd


def fiscal_period(period_end: date, fye_month: int = 12) -> tuple[int, int]:
    """The (fiscal year, fiscal quarter) of a quarter ending on period_end.

    Fiscal years are named by the calendar year they end in, which is the usual convention.
    """
    month, year = period_end.month, period_end.year
    quarter = ((month - fye_month - 1) % 12) // 3 + 1
    fiscal_year = year if month <= fye_month else year + 1
    return fiscal_year, quarter


def next_period(fiscal_year: int, quarter: int) -> tuple[int, int]:
    return (fiscal_year, quarter + 1) if quarter < 4 else (fiscal_year + 1, 1)


def month_end(day) -> date:
    """Move a date to the last day of its month (Sep 28 -> Sep 30)."""
    return (pd.Timestamp(day) + pd.offsets.MonthEnd(0)).date()


def quarter_end_after(period_end: date, quarters: int = 1) -> date:
    """The quarter end that comes `quarters` quarters after period_end."""
    return (pd.Timestamp(month_end(period_end)) + pd.offsets.MonthEnd(3 * quarters)).date()
