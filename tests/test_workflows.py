"""Tests for adherence, migration inventory, and roundtrip (TASK-0034/0031/0032)."""

from __future__ import annotations

import pytest

from yourtrainer_mcp import workflows
from yourtrainer_mcp import workout as wk
from yourtrainer_mcp.adherence import adherence_scorecard

WORKOUT = wk.build_workout({
    "name": "Steady",
    "steps": [
        {"kind": "steady", "duration_s": 300, "power": 0.8},
        {"kind": "steady", "duration_s": 300, "power": 0.6},
    ],
})


def test_adherence_perfect_when_actual_matches_plan():
    ftp = 250.0
    actual = [0.8 * ftp] * 300 + [0.6 * ftp] * 300
    out = adherence_scorecard(WORKOUT, actual, ftp)
    assert out["compliance_pct"] == pytest.approx(100.0)
    assert all(s.get("in_tolerance") for s in out["steps"] if "in_tolerance" in s)


def test_adherence_low_when_actual_too_easy():
    ftp = 250.0
    actual = [0.5 * ftp] * 600  # well below both targets
    out = adherence_scorecard(WORKOUT, actual, ftp)
    assert out["compliance_pct"] < 60
    first = out["steps"][0]
    assert first["deviation_pct"] < 0  # under target


def test_adherence_rejects_bad_ftp():
    with pytest.raises(ValueError):
        adherence_scorecard(WORKOUT, [200.0], ftp=0)


def test_migration_inventory_flags_conversions(tmp_path):
    (tmp_path / "a.zwo").write_text("<workout_file><workout></workout></workout_file>")
    (tmp_path / "b.ytw").write_text('{"format":"ytw","steps":[]}')
    (tmp_path / "c.gpx").write_text("<gpx></gpx>")
    paths = [str(tmp_path / n) for n in ("a.zwo", "b.ytw", "c.gpx")]
    out = workflows.migration_inventory(paths, target_format="ytw")
    assert out["files"] == 3
    # .zwo is a workout needing conversion; .ytw already target; .gpx not a workout.
    assert out["needs_conversion"] == 1
    by_file = {i["file"]: i for i in out["items"]}
    assert by_file["a.zwo"]["needs_conversion"] is True
    assert by_file["b.ytw"]["needs_conversion"] is False
    assert by_file["c.gpx"]["is_workout"] is False


def test_roundtrip_lossless_zwo_to_ytw():
    zwo = wk.to_zwo(WORKOUT)
    ytw = wk.to_ytw(wk.from_zwo(zwo))
    out = workflows.roundtrip_workout(zwo, "zwo", ytw, "ytw")
    assert out["lossless"] is True
    assert out["duration_match"] is True
    assert out["max_deviation_w"] <= 0.5


def test_roundtrip_detects_loss():
    zwo = wk.to_zwo(WORKOUT)
    shorter = wk.to_ytw(wk.build_workout({"name": "x", "steps": [
        {"kind": "steady", "duration_s": 300, "power": 0.8}]}))
    out = workflows.roundtrip_workout(zwo, "zwo", shorter, "ytw")
    assert out["lossless"] is False
    assert out["duration_match"] is False
