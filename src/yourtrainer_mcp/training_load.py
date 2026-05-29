"""Multi-ride training-load math (TASK-0027, TASK-0051).

CTL / ATL / TSB (fitness / fatigue / form) as exponentially-weighted moving
averages of daily TSS, plus a recovery-time heuristic. Pure Python.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

CTL_TIME_CONSTANT = 42  # days ("fitness")
ATL_TIME_CONSTANT = 7  # days ("fatigue")


def _ewma_step(prev: float, today: float, time_constant: int) -> float:
    alpha = 1.0 - math.exp(-1.0 / time_constant)
    return prev + (today - prev) * alpha


def training_load_series(
    daily_tss: list[float],
    ctl_tc: int = CTL_TIME_CONSTANT,
    atl_tc: int = ATL_TIME_CONSTANT,
    ctl_seed: float = 0.0,
    atl_seed: float = 0.0,
) -> list[dict]:
    """Compute CTL/ATL/TSB over a dense daily TSS series (one value per day).

    TSB (form) is reported as the *previous day's* CTL−ATL, the standard
    convention (today's form reflects yesterday's fitness minus fatigue).
    """
    out: list[dict] = []
    ctl, atl = ctl_seed, atl_seed
    for i, tss in enumerate(daily_tss):
        tsb = ctl - atl  # previous day's balance, before today's update
        ctl = _ewma_step(ctl, tss, ctl_tc)
        atl = _ewma_step(atl, tss, atl_tc)
        out.append({
            "day": i,
            "tss": round(tss, 1),
            "ctl": round(ctl, 1),
            "atl": round(atl, 1),
            "tsb": round(tsb, 1),
        })
    return out


def densify_daily_tss(dated_tss: list[tuple[str, float]]) -> tuple[list[float], list[str]]:
    """Turn sparse ``(iso_date, tss)`` pairs into a dense daily series.

    Multiple activities on the same day sum. Missing days are filled with 0.
    Returns ``(tss_per_day, iso_date_per_day)`` spanning first..last date.
    """
    if not dated_tss:
        return [], []
    by_day: dict[date, float] = {}
    for iso, tss in dated_tss:
        d = date.fromisoformat(iso[:10])
        by_day[d] = by_day.get(d, 0.0) + tss
    start, end = min(by_day), max(by_day)
    series: list[float] = []
    dates: list[str] = []
    cur = start
    while cur <= end:
        series.append(by_day.get(cur, 0.0))
        dates.append(cur.isoformat())
        cur += timedelta(days=1)
    return series, dates


def training_load_from_dated_tss(dated_tss: list[tuple[str, float]]) -> dict:
    """Full CTL/ATL/TSB report from sparse dated TSS values."""
    series, dates = densify_daily_tss(dated_tss)
    rows = training_load_series(series)
    for row, iso in zip(rows, dates, strict=True):
        row["date"] = iso
    final = rows[-1] if rows else {"ctl": 0.0, "atl": 0.0, "tsb": 0.0}
    return {
        "days": len(rows),
        "ctl": final["ctl"],
        "atl": final["atl"],
        "tsb": final["tsb"],
        "series": rows,
    }


# Recovery-time heuristic (TASK-0051). A single session's TSS maps to a coarse
# recovery window. This is a rule-of-thumb, not a physiological measurement.
_RECOVERY_BANDS = (
    (150, "low", 24),
    (300, "moderate", 36),
    (450, "high", 60),
    (float("inf"), "very high", 84),
)


def recovery_estimate(tss: float) -> dict:
    """Estimate recovery from a single session's TSS."""
    for upper, label, hours in _RECOVERY_BANDS:
        if tss < upper:
            return {"tss": round(tss, 1), "strain": label, "estimated_recovery_hours": hours}
    raise AssertionError("unreachable")  # pragma: no cover
