"""Agent step 5: turn the facts into a recommendation, using fixed rules.

No AI in this file. The same inputs always give the same answer, and every
answer names the rule that produced it.

Rules for each metric (checked in this order; the first that applies wins):
  R0  The figure is missing or failed a check          -> NEEDS REVIEW
  R1  We have no estimate to compare against           -> NEEDS REVIEW
  R2  The variance is smaller than the threshold       -> HOLD
  R5  Big variance, cause unclear or quote unverified  -> NEEDS REVIEW
  R3  Big variance, caused by a one-time item          -> HOLD
  R4  Big variance, caused by the ongoing business     -> REVISE UP / REVISE DOWN

Rules for the overall call:
  R6  The release contains suspicious text             -> NEEDS REVIEW
  R7  Revenue or EPS needs review, or guidance was withdrawn -> NEEDS REVIEW
  R8  Signals point in opposite directions             -> NEEDS REVIEW
  R9  Otherwise follow revenue, EPS and guidance: any up -> REVISE UP,
      any down -> REVISE DOWN, none -> HOLD
"""

from dataclasses import asdict, dataclass

from agent.config import CARRY_THROUGH
from agent.schemas import KEY_METRICS, Driver, Guidance
from agent.variance import Variance

REVISE_UP, REVISE_DOWN, HOLD, NEEDS_REVIEW = "REVISE UP", "REVISE DOWN", "HOLD", "NEEDS REVIEW"


@dataclass
class MetricCall:
    metric: str
    call: str
    rule: str
    reason: str
    suggested_change_pct: float | None = None  # suggested change to forward estimates

    def to_dict(self) -> dict:
        return asdict(self)


def decide_metric(
    variance: Variance,
    figure_verified: bool,
    driver: Driver | None,
    driver_quote_verified: bool,
    carry_through: float = CARRY_THROUGH,
) -> MetricCall:
    metric = variance.metric
    if not figure_verified or variance.actual is None:
        return MetricCall(metric, NEEDS_REVIEW, "R0", "The reported figure is missing or failed a check.")
    if variance.estimate is None:
        return MetricCall(metric, NEEDS_REVIEW, "R1", "No estimate on file to compare against.")
    if not variance.flagged:
        return MetricCall(metric, HOLD, "R2", f"Variance of {variance.pct:+.1f}% is inside the threshold.")
    if driver is None or driver.kind == "unclear" or not driver_quote_verified or variance.pct is None:
        return MetricCall(metric, NEEDS_REVIEW, "R5", "Large variance, but the cause is unclear or unverified.")
    if driver.kind == "one_time":
        return MetricCall(metric, HOLD, "R3", f"Variance of {variance.pct:+.1f}% comes from a one-time item.")
    call = REVISE_UP if variance.pct > 0 else REVISE_DOWN
    return MetricCall(
        metric, call, "R4",
        f"Variance of {variance.pct:+.1f}% comes from the ongoing business.",
        round(variance.pct * carry_through, 1),
    )


def decide_overall(calls: list[MetricCall], guidance: Guidance, suspicious_text: list[str]) -> dict:
    """Combine the per-metric calls into one headline call with a confidence level."""
    by_metric = {c.metric: c for c in calls}
    key_calls = [by_metric[m] for m in KEY_METRICS if m in by_metric]
    other_needs_review = any(c.call == NEEDS_REVIEW for c in calls if c.metric not in KEY_METRICS)

    def result(call, rule, reason, confidence):
        return {"call": call, "rule": rule, "reason": reason, "confidence": confidence}

    if suspicious_text:
        return result(NEEDS_REVIEW, "R6", "The release contains text that looks like instructions to an AI.", "low")
    if any(c.call == NEEDS_REVIEW for c in key_calls):
        return result(NEEDS_REVIEW, "R7", "Revenue or EPS could not be decided automatically.", "low")
    if guidance.status == "withdrawn":
        return result(NEEDS_REVIEW, "R7", "Management withdrew its guidance.", "low")

    up = any(c.call == REVISE_UP for c in key_calls) or guidance.status == "raised"
    down = any(c.call == REVISE_DOWN for c in key_calls) or guidance.status == "lowered"
    if up and down:
        return result(NEEDS_REVIEW, "R8", "Results and guidance point in opposite directions.", "low")

    confidence = "medium" if other_needs_review else "high"
    if up:
        return result(REVISE_UP, "R9", "Recurring beat and/or raised guidance.", confidence)
    if down:
        return result(REVISE_DOWN, "R9", "Recurring miss and/or lowered guidance.", confidence)
    return result(HOLD, "R9", "No recurring surprise in revenue or EPS and no guidance change.", confidence)
