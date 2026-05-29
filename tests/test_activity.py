"""Tests for activity parsing + the inspector (TASK-0021, TST-0001)."""

from __future__ import annotations

import pytest

from yourtrainer_mcp.activity import (
    UnsupportedActivityFormat,
    inspect_activity,
    parse_activity_file,
    parse_gpx,
    parse_tcx,
)


def test_parse_tcx_reads_power_hr_cadence(tcx_builder):
    text = tcx_builder([250.0] * 10)
    points = parse_tcx(text)
    assert len(points) == 10
    assert points[0].power_w == 250.0
    assert points[0].heart_rate_bpm == 140.0
    assert points[0].cadence_rpm == 90.0
    assert points[0].time is not None


def test_parse_gpx_reads_power_extension(gpx_builder):
    text = gpx_builder([200.0] * 5)
    points = parse_gpx(text)
    assert len(points) == 5
    assert points[0].power_w == 200.0
    assert points[0].altitude_m == 100.0


def test_inspect_tcx_canonical_hour_at_ftp(tcx_builder, tmp_path):
    # 3600 s constant at FTP -> NP == FTP, IF == 1.0, TSS == 100.
    text = tcx_builder([250.0] * 3601)  # 3601 points -> 3600 s elapsed
    f = tmp_path / "ride.tcx"
    f.write_text(text, encoding="utf-8")
    points = parse_activity_file(f)
    summary = inspect_activity(points, ftp=250.0)
    assert summary["power"]["normalized_power_w"] == pytest.approx(250.0, abs=0.5)
    assert summary["power"]["intensity_factor"] == pytest.approx(1.0, abs=0.01)
    assert summary["power"]["training_stress_score"] == pytest.approx(100.0, abs=1.0)
    assert summary["duration_s"] == pytest.approx(3600.0, abs=0.5)


def test_inspect_reports_hr_cadence_and_distance(tcx_builder):
    points = parse_tcx(tcx_builder([200.0] * 60))
    summary = inspect_activity(points, ftp=250.0)
    assert summary["heart_rate"]["avg_bpm"] is not None
    assert summary["cadence"]["avg_rpm"] == pytest.approx(90.0)
    # 60 points, +10 m each after the first -> ~590-600 m span.
    assert summary["distance_m"] > 0


def test_inspect_elevation_gain(tcx_builder):
    altitudes = [100.0 + i for i in range(50)] + [149.0] * 10  # +49 then flat
    points = parse_tcx(tcx_builder([200.0] * 60, altitudes=altitudes))
    summary = inspect_activity(points, ftp=250.0)
    assert summary["elevation_gain_m"] == pytest.approx(49.0, abs=0.5)


def test_inspect_route_without_power(gpx_builder):
    # Plain route: no power data -> power block is None, distance from lat/lon.
    points = parse_gpx(gpx_builder(n=20))
    summary = inspect_activity(points, ftp=250.0)
    assert summary["power"] is None
    assert summary["distance_m"] > 0


def test_inspect_rejects_non_positive_ftp(tcx_builder):
    points = parse_tcx(tcx_builder([200.0] * 10))
    with pytest.raises(ValueError):
        inspect_activity(points, ftp=0)


def test_unsupported_format_raises(tmp_path):
    f = tmp_path / "ride.xyz"
    f.write_text("nope", encoding="utf-8")
    with pytest.raises(UnsupportedActivityFormat):
        parse_activity_file(f)
