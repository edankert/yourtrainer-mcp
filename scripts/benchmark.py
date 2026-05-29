#!/usr/bin/env python3
"""Standalone performance benchmark (TASK-0044).

Prints timings for the hot paths so a baseline can be recorded and compared
over time. Not run in CI (the budget assertions in tests/test_performance.py
guard against regressions there). Run: ``python scripts/benchmark.py``.
"""

from __future__ import annotations

import time

from yourtrainer_mcp import analysis
from yourtrainer_mcp import power as pw
from yourtrainer_mcp import workout as wk
from yourtrainer_mcp.activity import TrackPoint, inspect_activity


def _time(label: str, fn, repeats: int = 5) -> None:
    best = min(_once(fn) for _ in range(repeats))
    print(f"{label:<42} {best * 1000:8.2f} ms (best of {repeats})")


def _once(fn) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def main() -> None:
    hour_power = [200.0 + (i % 120) for i in range(3600)]
    points = [TrackPoint(power_w=200.0 + (i % 50), heart_rate_bpm=150.0,
                         cadence_rpm=90.0) for i in range(3600)]
    intent = {"name": "bench", "steps": [
        {"kind": "interval", "repeat": 20, "on_duration_s": 60, "off_duration_s": 60,
         "on_power": 1.1, "off_power": 0.5}]}

    print("yourtrainer-mcp benchmark (3600-sample / 1-hour inputs)\n" + "-" * 60)
    _time("normalized_power (1h)", lambda: pw.normalized_power(hour_power))
    _time("peak_power_curve (1h)", lambda: analysis.peak_power_curve(hour_power))
    _time("inspect_activity (1h)", lambda: inspect_activity(points, 250.0))
    _time("detect_intervals (1h)", lambda: analysis.detect_intervals(hour_power, 250.0))
    _time("build+difficulty+zwo", lambda: _build(intent))


def _build(intent: dict) -> None:
    w = wk.build_workout(intent)
    wk.difficulty_score(w, 250.0)
    wk.to_zwo(w)


if __name__ == "__main__":
    main()
