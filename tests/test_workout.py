"""Tests for the workout authoring cluster (TASK-0023/0033/0035/0025/0050/0024)."""

from __future__ import annotations

import json

import pytest

from yourtrainer_mcp import workout as wk

INTENT = {
    "name": "Sweet Spot 2x20",
    "description": "Classic sweet-spot session",
    "author": "tester",
    "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.7},
        {"kind": "steady", "duration_s": 1200, "power": 0.9, "cadence": 90},
        {"kind": "steady", "duration_s": 300, "power": 0.5},
        {"kind": "interval", "repeat": 4, "on_duration_s": 60, "off_duration_s": 60,
         "on_power": 1.2, "off_power": 0.5},
        {"kind": "cooldown", "duration_s": 600, "power_low": 0.6, "power_high": 0.4},
    ],
}


def test_build_and_total_duration():
    w = wk.build_workout(INTENT)
    # 600 + 1200 + 300 + 4*(60+60) + 600 = 3180
    assert w.total_duration_s() == 3180
    assert w.name == "Sweet Spot 2x20"


def test_build_rejects_missing_fields():
    with pytest.raises(wk.WorkoutError):
        wk.build_workout({"steps": [{"kind": "steady", "duration_s": 60}]})  # no power
    with pytest.raises(wk.WorkoutError):
        wk.build_workout({"steps": [{"kind": "bogus"}]})
    with pytest.raises(wk.WorkoutError):
        wk.build_workout({"steps": []})


def test_zwo_roundtrip_preserves_structure():
    w = wk.build_workout(INTENT)
    zwo = wk.to_zwo(w)
    assert "<workout_file>" in zwo and "IntervalsT" in zwo
    back = wk.from_zwo(zwo)
    assert back.total_duration_s() == w.total_duration_s()
    assert [s.kind for s in back.steps] == [s.kind for s in w.steps]
    assert back.steps[3].repeat == 4
    assert back.steps[1].power == pytest.approx(0.9)


def test_ytw_roundtrip_preserves_structure():
    w = wk.build_workout(INTENT)
    ytw = wk.to_ytw(w)
    doc = json.loads(ytw)
    assert doc["format"] == "ytw" and doc["version"] == wk.YTW_VERSION
    back = wk.from_ytw(ytw)
    assert back.total_duration_s() == w.total_duration_s()
    assert [s.kind for s in back.steps] == [s.kind for s in w.steps]
    assert back.steps[1].cadence == 90


def test_from_ytw_rejects_non_ytw():
    with pytest.raises(wk.WorkoutError):
        wk.from_ytw(json.dumps({"format": "nope"}))


def test_scale_duration_halves_all_steps():
    w = wk.build_workout(INTENT)
    half = wk.scale_workout(w, duration_factor=0.5)
    assert half.total_duration_s() == pytest.approx(w.total_duration_s() / 2, abs=2)
    assert "50% duration" in half.name


def test_scale_intensity_raises_power_not_duration():
    w = wk.build_workout(INTENT)
    harder = wk.scale_workout(w, intensity_factor=1.1)
    assert harder.total_duration_s() == w.total_duration_s()
    # steady step 0.9 -> 0.99
    steady = next(s for s in harder.steps if s.kind == "steady")
    assert steady.power == pytest.approx(0.99)


def test_scale_rejects_non_positive():
    w = wk.build_workout(INTENT)
    with pytest.raises(wk.WorkoutError):
        wk.scale_workout(w, duration_factor=0)


def test_difficulty_score_reasonable():
    w = wk.build_workout(INTENT)
    score = wk.difficulty_score(w, ftp=250.0)
    assert score["duration_s"] == 3180
    assert 0 < score["intensity_factor"] < 1.2
    assert score["tss"] > 0
    # FTP-independence: TSS identical for a different FTP.
    assert score["tss"] == pytest.approx(wk.difficulty_score(w, ftp=300.0)["tss"], abs=0.1)


def test_lint_flags_missing_warmup_and_zero_duration():
    bad = wk.Workout(name="", steps=[wk.Step("steady", duration_s=0, power=0.8)])
    findings = wk.lint_workout(bad)
    codes = {f["code"] for f in findings}
    assert "zero-duration" in codes
    assert "no-warmup" in codes
    assert "no-name" in codes


def test_lint_clean_workout_has_no_errors():
    w = wk.build_workout(INTENT)
    findings = wk.lint_workout(w)
    assert not [f for f in findings if f["severity"] == "error"]


def test_lint_flags_implausible_power():
    w = wk.Workout(name="x", steps=[
        wk.Step("warmup", 60, power_low=0.4, power_high=0.6),
        wk.Step("steady", 60, power=9.0),
    ])
    codes = {f["code"] for f in wk.lint_workout(w)}
    assert "power-range" in codes


def test_app_acceptance_flags_freeride_on_garmin():
    w = wk.Workout(name="x", steps=[
        wk.Step("warmup", 60, power_low=0.4, power_high=0.6),
        wk.Step("freeride", 600),
    ])
    result = wk.app_acceptance(w)
    assert result["garmin_edge"]["accepted"] is False
    assert result["zwift"]["accepted"] is True


def test_app_acceptance_flags_long_name_on_garmin():
    w = wk.Workout(name="x" * 40, steps=[wk.Step("steady", 60, power=0.8)])
    result = wk.app_acceptance(w, apps=["garmin_edge"])
    assert result["garmin_edge"]["accepted"] is False
    assert any("Name exceeds" in i for i in result["garmin_edge"]["issues"])
