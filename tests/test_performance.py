"""Performance baselines / regression detection (TASK-0044).

Budgets are deliberately generous (~10× expected) so they don't flake on slow
CI runners — their job is to catch *pathological* regressions (e.g. an
accidental O(n²) in the power math), not to micro-benchmark.
"""

from __future__ import annotations

import time

import pytest

from yourtrainer_mcp import analysis
from yourtrainer_mcp import power as pw
from yourtrainer_mcp import workout as wk
from yourtrainer_mcp.activity import TrackPoint, inspect_activity

HOUR = 3600


def _elapsed(fn) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def test_normalized_power_hour_is_fast():
    power = [200.0 + (i % 100) for i in range(HOUR)]
    assert _elapsed(lambda: pw.normalized_power(power)) < 1.0


def test_peak_power_curve_hour_is_fast():
    power = [200.0 + (i % 100) for i in range(HOUR)]
    assert _elapsed(lambda: analysis.peak_power_curve(power)) < 2.0


def test_inspect_hour_activity_is_fast():
    points = [TrackPoint(power_w=200.0 + (i % 50), heart_rate_bpm=150.0,
                         cadence_rpm=90.0) for i in range(HOUR)]
    assert _elapsed(lambda: inspect_activity(points, 250.0)) < 3.0


def test_interval_detection_hour_is_fast():
    power = ([300.0] * 120 + [120.0] * 120) * 15  # 3600 samples
    assert _elapsed(lambda: analysis.detect_intervals(power, 250.0)) < 2.0


def test_build_and_score_is_fast():
    intent = {"name": "perf", "steps": [
        {"kind": "interval", "repeat": 20, "on_duration_s": 60, "off_duration_s": 60,
         "on_power": 1.1, "off_power": 0.5}]}

    def go():
        w = wk.build_workout(intent)
        wk.difficulty_score(w, 250.0)
        wk.to_zwo(w)

    assert _elapsed(go) < 1.0


@pytest.mark.parametrize("n", [600, 3600, 18000])
def test_normalized_power_scales_linearly(n):
    # A 5-hour ride should still complete comfortably; guards against O(n^2).
    power = [200.0] * n
    assert _elapsed(lambda: pw.normalized_power(power)) < 3.0
