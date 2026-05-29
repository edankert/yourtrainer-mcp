"""Tests for the self-contained FIT codec (TASK-0020) and FIT-read (TASK-0021).

All hermetic — no external FIT files or the fitparse extra required.
"""

from __future__ import annotations

import pytest

from yourtrainer_mcp import fit, fit_workout
from yourtrainer_mcp import workout as wk
from yourtrainer_mcp.activity import inspect_activity, parse_activity_file

INTENT = {
    "name": "FIT 5x3",
    "description": "FIT codec test",
    "warmup": {"duration_seconds": 600, "zone": "Z2", "label": "Warmup",
               "target_power_percent": 40, "target_power_end_percent": 70},
    "intervals": [
        {"repeat": 5, "intervals": [
            {"duration_seconds": 180, "zone": "Z5", "label": "On", "target_power_percent": 110},
            {"duration_seconds": 180, "zone": "Z1", "label": "Off", "target_power_percent": 50}]},
        {"duration_seconds": 300, "zone": "Z2", "label": "Steady", "target_power_percent": 65},
    ],
    "cooldown": {"duration_seconds": 600, "zone": "Z1", "label": "Cooldown",
                 "target_power_percent": 60, "target_power_end_percent": 40},
}


def test_fit_file_has_valid_signature_and_crc():
    w = wk.build_workout(INTENT)
    data = fit_workout.encode_workout_fit(w)
    assert data[8:12] == b".FIT"
    # File CRC is the last 2 bytes over everything preceding.
    body_crc = fit.crc16(data[:-2])
    assert body_crc == int.from_bytes(data[-2:], "little")
    # Header CRC over the first 12 bytes.
    assert fit.crc16(data[:12]) == int.from_bytes(data[12:14], "little")


def test_workout_fit_roundtrip_preserves_power_profile():
    w = wk.build_workout(INTENT)
    data = fit_workout.encode_workout_fit(w)
    back = fit_workout.decode_workout_fit(data)
    # Interval/ramp expansion makes step lists differ; the per-second power
    # series must match (lossless under FIT %FTP integer quantisation).
    s1 = wk.expand_to_power_series(w, ftp=250.0)
    s2 = wk.expand_to_power_series(back, ftp=250.0)
    assert len(s1) == len(s2)
    # Integer % FTP -> exact round-trip (no quantisation loss).
    assert s1 == s2
    assert back.name == "FIT 5x3"


def test_workout_fit_step_count_matches_flattened():
    w = wk.build_workout(INTENT)
    back = fit_workout.decode_workout_fit(fit_workout.encode_workout_fit(w))
    # warmup(1) + 5*(on+off)=10 + steady(1) + cooldown(1) = 13 flattened blocks
    assert len(back.intervals) == 13
    assert back.intervals[-1].interval_type == "COOLDOWN"
    assert back.intervals[0].interval_type == "WARMUP"


def test_decode_rejects_non_fit():
    with pytest.raises(ValueError):
        fit.decode(b"not a fit file at all")


def test_fit_activity_read_through_inspector(tmp_path):
    # Generate a FIT activity fixture: constant 250 W for an hour.
    samples = [{"power": 250, "heart_rate": 150, "cadence": 90} for _ in range(3600)]
    data = fit.encode_activity_fit(samples)
    f = tmp_path / "ride.fit"
    f.write_bytes(data)
    points = parse_activity_file(f)  # uses built-in fallback (no fitparse needed)
    assert len(points) == 3600
    summary = inspect_activity(points, ftp=250.0)
    assert summary["power"]["normalized_power_w"] == pytest.approx(250.0, abs=0.5)
    assert summary["power"]["intensity_factor"] == pytest.approx(1.0, abs=0.01)
    assert summary["power"]["training_stress_score"] == pytest.approx(100.0, abs=1.0)
    assert summary["heart_rate"]["avg_bpm"] == pytest.approx(150.0)


def test_fit_activity_distance_and_altitude_scaling(tmp_path):
    samples = [
        {"power": 200, "distance_m": i * 10.0, "altitude_m": 100.0 + i, "speed_mps": 10.0}
        for i in range(30)
    ]
    f = tmp_path / "ride2.fit"
    f.write_bytes(fit.encode_activity_fit(samples))
    points = parse_activity_file(f)
    summary = inspect_activity(points, ftp=250.0)
    # distance spans 0..290 m; elevation climbs ~29 m.
    assert summary["distance_m"] == pytest.approx(290.0, abs=1.0)
    assert summary["elevation_gain_m"] == pytest.approx(29.0, abs=1.0)
