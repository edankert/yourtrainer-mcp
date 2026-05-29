"""Tests for CTL/ATL/TSB + recovery (TASK-0027, TASK-0051)."""

from __future__ import annotations

import pytest

from yourtrainer_mcp import training_load as tl


def test_constant_tss_converges_toward_that_value():
    rows = tl.training_load_series([100.0] * 200)
    # After many days at 100 TSS/day, CTL and ATL approach 100.
    assert rows[-1]["ctl"] == pytest.approx(100.0, abs=1.0)
    assert rows[-1]["atl"] == pytest.approx(100.0, abs=0.5)
    # At equilibrium, form (TSB) approaches 0.
    assert abs(rows[-1]["tsb"]) < 1.0


def test_atl_responds_faster_than_ctl():
    # A single hard day after rest: fatigue (ATL) jumps more than fitness (CTL).
    rows = tl.training_load_series([0.0] * 10 + [300.0])
    assert rows[-1]["atl"] > rows[-1]["ctl"]


def test_densify_fills_gaps_and_sums_same_day():
    series, dates = tl.densify_daily_tss(
        [("2026-05-01", 50), ("2026-05-01", 30), ("2026-05-04", 80)]
    )
    assert dates == ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"]
    assert series == [80.0, 0.0, 0.0, 80.0]  # day 1 summed, gaps zero


def test_training_load_from_dated_tss_reports_final():
    out = tl.training_load_from_dated_tss([("2026-05-01", 100), ("2026-05-02", 100)])
    assert out["days"] == 2
    assert "ctl" in out and "atl" in out and "tsb" in out
    assert out["series"][0]["date"] == "2026-05-01"


def test_empty_input():
    assert tl.densify_daily_tss([]) == ([], [])
    assert tl.training_load_from_dated_tss([])["days"] == 0


@pytest.mark.parametrize(
    "tss,label,hours",
    [(100, "low", 24), (200, "moderate", 36), (400, "high", 60), (500, "very high", 84)],
)
def test_recovery_bands(tss, label, hours):
    r = tl.recovery_estimate(tss)
    assert r["strain"] == label
    assert r["estimated_recovery_hours"] == hours
