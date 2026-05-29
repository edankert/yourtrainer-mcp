"""Unit tests for the power / training-load math (TASK-0021, TST-0001).

Validated against analytically-known and canonical reference values:
- Constant power => NP == power.
- 1 hour at FTP => IF 1.0, TSS 100 (the canonical TrainingPeaks anchor).
- Variable power => NP > average power.
"""

from __future__ import annotations

import math

import pytest

from yourtrainer_mcp import power as pw


def test_rolling_average_basic():
    assert pw.rolling_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_rolling_average_shorter_than_window_returns_mean():
    assert pw.rolling_average([2, 4], 30) == [3.0]


def test_constant_power_np_equals_power():
    power = [250.0] * 3600
    assert pw.normalized_power(power) == pytest.approx(250.0, abs=1e-6)


def test_canonical_one_hour_at_ftp_is_100_tss():
    ftp = 250.0
    power = [ftp] * 3600
    np_value = pw.normalized_power(power)
    if_value = pw.intensity_factor(np_value, ftp)
    tss = pw.training_stress_score(3600, np_value, ftp)
    assert if_value == pytest.approx(1.0, abs=1e-6)
    assert tss == pytest.approx(100.0, abs=1e-3)


def test_tss_identity_matches_if_squared_form():
    # TSS == (duration_h) * IF^2 * 100
    ftp, np_value, duration = 250.0, 300.0, 1800.0
    tss = pw.training_stress_score(duration, np_value, ftp)
    if_value = np_value / ftp
    assert tss == pytest.approx((duration / 3600) * if_value**2 * 100, rel=1e-9)


def test_variable_power_np_exceeds_average():
    # 30 min hard / easy alternating blocks.
    power = ([300.0] * 300 + [100.0] * 300) * 3
    np_value = pw.normalized_power(power)
    assert np_value > pw.average(power)


def test_np_known_small_value():
    # Window collapses to the full-series mean when shorter than 30 s,
    # so NP == mean of the single rolling value == arithmetic mean here.
    power = [100.0, 300.0]
    # rolling avg over 30 s window on 2 samples -> [200.0]; NP == 200.
    assert pw.normalized_power(power) == pytest.approx(200.0, abs=1e-6)


def test_peak_power_curve_constant():
    power = [200.0] * 100
    ppc = pw.peak_power_curve(power, durations_s=(1, 5, 30, 60))
    assert ppc == {1: 200.0, 5: 200.0, 30: 200.0, 60: 200.0}


def test_peak_power_curve_omits_too_long_durations():
    power = [200.0] * 10
    ppc = pw.peak_power_curve(power, durations_s=(1, 60))
    assert 60 not in ppc
    assert ppc[1] == 200.0


def test_peak_power_curve_finds_the_best_window():
    power = [100.0] * 50 + [400.0] * 10 + [100.0] * 50
    ppc = pw.peak_power_curve(power, durations_s=(5,))
    assert ppc[5] == pytest.approx(400.0)


def test_time_in_zone_constant_tempo():
    # 200 W at FTP 250 -> 0.8 of FTP -> Z3 Tempo (upper bound 0.90).
    power = [200.0] * 600
    tiz = pw.time_in_zone(power, ftp=250.0)
    assert tiz["Z3 Tempo"] == pytest.approx(600.0)
    assert sum(tiz.values()) == pytest.approx(600.0)


def test_intensity_factor_and_tss_reject_bad_ftp():
    with pytest.raises(ValueError):
        pw.intensity_factor(200.0, 0)
    with pytest.raises(ValueError):
        pw.training_stress_score(3600, 200.0, -1)


def test_empty_power_is_zero_np():
    assert pw.normalized_power([]) == 0.0
    assert not math.isnan(pw.normalized_power([]))
