"""Tests for single-ride analytics (TASK-0022/0028/0036/0046/0047/0052/0053/0054)."""

from __future__ import annotations

import pytest

from yourtrainer_mcp import analysis


def test_best_efforts_reports_watts_and_timing():
    power = [100.0] * 50 + [400.0] * 10 + [100.0] * 50
    be = analysis.best_efforts(power, durations_s=(5, 10))
    assert be[5]["watts"] == pytest.approx(400.0)
    assert be[5]["start_s"] == pytest.approx(50.0, abs=1.0)


def test_estimate_ftp_uses_20min_when_no_hour():
    power = [200.0] * 1300  # >20 min, <60 min
    out = analysis.estimate_ftp(power)
    assert out["method"] == "best_20min_x0.95"
    assert out["ftp_w"] == pytest.approx(190.0, abs=0.5)


def test_estimate_ftp_uses_hour_when_available():
    power = [200.0] * 3700
    out = analysis.estimate_ftp(power)
    assert out["method"] == "best_60min"
    assert out["ftp_w"] == pytest.approx(200.0, abs=0.5)


def test_estimate_ftp_insufficient_data():
    assert analysis.estimate_ftp([200.0] * 100)["ftp_w"] is None


def test_power_duration_model_constant_power_gives_flat_cp():
    # Constant power -> all mean-max equal -> CP == power, W' ~ 0.
    power = [200.0] * 1300
    m = analysis.power_duration_model(power)
    assert m["cp_w"] == pytest.approx(200.0, abs=1.0)
    assert abs(m["w_prime_j"]) < 1.0
    assert m["method"] == "2-param-cp"


def test_power_duration_model_insufficient():
    assert analysis.power_duration_model([200.0] * 60)["cp_w"] is None


def test_hr_power_decoupling_positive_when_hr_drifts_up():
    power = [200.0] * 100
    hr = [140.0] * 50 + [160.0] * 50
    out = analysis.hr_power_decoupling(power, hr)
    # ef1=200/140, ef2=200/160 -> ~12.5% decoupling.
    assert out["decoupling_pct"] == pytest.approx(12.5, abs=0.5)
    assert out["well_paced"] is False


def test_hr_power_decoupling_well_paced():
    power = [200.0] * 100
    hr = [150.0] * 100
    out = analysis.hr_power_decoupling(power, hr)
    assert out["decoupling_pct"] == pytest.approx(0.0, abs=0.01)
    assert out["well_paced"] is True


def test_hr_drift_reports_halves_and_aerobic_estimate():
    hr = [140.0] * 50 + [150.0] * 50
    out = analysis.hr_drift(hr)
    assert out["hr_drift_pct"] == pytest.approx(7.14, abs=0.2)
    assert out["approx_aerobic_hr"] > 0


def test_cadence_analysis_bands_and_coasting():
    cadence = [0.0] * 10 + [95.0] * 90
    out = analysis.cadence_analysis(cadence)
    assert out["coasting_pct"] == pytest.approx(10.0)
    assert out["avg_rpm_moving"] == pytest.approx(95.0)
    assert out["time_in_band_s"]["90-99"] == pytest.approx(90.0)


def test_detect_intervals_finds_a_work_block():
    # 5 min easy, 4 min hard, 5 min easy at FTP 250.
    power = [120.0] * 300 + [280.0] * 240 + [120.0] * 300
    efforts = analysis.detect_intervals(power, ftp=250.0)
    assert len(efforts) == 1
    assert efforts[0]["duration_s"] == pytest.approx(240.0, abs=15.0)
    assert efforts[0]["avg_w"] == pytest.approx(280.0, abs=5.0)


def test_detect_intervals_rejects_bad_ftp():
    with pytest.raises(ValueError):
        analysis.detect_intervals([200.0], ftp=0)


def test_detect_intervals_empty():
    assert analysis.detect_intervals([], ftp=250.0) == []
