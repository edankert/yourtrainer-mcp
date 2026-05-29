"""Tests for route analytics: profile, climbs, pacing (TASK-0029, TASK-0048)."""

from __future__ import annotations

import pytest

from yourtrainer_mcp import route
from yourtrainer_mcp.activity import TrackPoint


def _climb_points(n=20, lat_step=0.001, alt_step=8.0):
    """A steady climb: ~111 m between points, +alt_step m each => ~8% grade."""
    return [TrackPoint(lat=52.0 + i * lat_step, lon=5.0, altitude_m=100.0 + i * alt_step)
            for i in range(n)]


def _flat_then_climb():
    flat = [TrackPoint(lat=52.0 + i * 0.001, lon=5.0, altitude_m=100.0) for i in range(10)]
    climb = [TrackPoint(lat=52.01 + i * 0.001, lon=5.0, altitude_m=100.0 + i * 8.0)
             for i in range(1, 20)]
    return flat + climb


def test_route_profile_distance_and_gain():
    prof = route.route_profile(_climb_points())
    assert prof["total_distance_m"] > 1500
    assert prof["elevation_gain_m"] == pytest.approx(152.0, abs=1.0)  # 19 steps * 8 m
    assert prof["elevation_loss_m"] == 0.0


def test_climb_analysis_detects_one_climb():
    out = route.climb_analysis(_flat_then_climb())
    assert out["climb_count"] == 1
    c = out["climbs"][0]
    assert 5.0 < c["avg_grade_pct"] < 9.0  # ~7% sustained climb
    assert c["category"] in {"1", "2", "3", "HC"}
    assert c["elevation_gain_m"] > 100


def test_climb_analysis_ignores_flat():
    flat = [TrackPoint(lat=52.0 + i * 0.001, lon=5.0, altitude_m=100.0) for i in range(20)]
    assert route.climb_analysis(flat)["climb_count"] == 0


def test_pacing_strategy_targets_climbs_harder():
    out = route.pacing_strategy(_flat_then_climb(), ftp_watts=250.0, target_intensity=0.7)
    assert out["base_target_w"] == pytest.approx(175.0)
    assert out["climb_targets"]
    # Climb target should exceed the flat base target.
    assert out["climb_targets"][0]["target_w"] > out["base_target_w"]
    # Capped at 1.15x FTP.
    assert out["climb_targets"][0]["target_w"] <= 1.15 * 250.0


def test_pacing_rejects_bad_ftp():
    with pytest.raises(ValueError):
        route.pacing_strategy(_climb_points(), ftp_watts=0)
