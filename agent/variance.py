"""Compares what the company reported with what we expected. Plain arithmetic only."""

from dataclasses import asdict, dataclass

from agent.config import FLAG_THRESHOLD_PCT


@dataclass
class Variance:
    metric: str
    estimate: float | None
    actual: float | None
    difference: float | None = None   # actual minus estimate
    pct: float | None = None          # difference as a percent of the estimate
    flagged: bool = False             # True when the gap is big enough to need a decision

    def to_dict(self) -> dict:
        return asdict(self)


def compute_variance(
    metric: str, estimate: float | None, actual: float | None, threshold_pct: float = FLAG_THRESHOLD_PCT
) -> Variance:
    if estimate is None or actual is None:
        return Variance(metric, estimate, actual)
    difference = round(actual - estimate, 4)
    if estimate == 0:
        # Can't take a percentage of zero; flag it so a person looks.
        return Variance(metric, estimate, actual, difference, None, True)
    pct = round(difference / abs(estimate) * 100, 2)
    return Variance(metric, estimate, actual, difference, pct, abs(pct) >= threshold_pct)
