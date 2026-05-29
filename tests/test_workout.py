"""Tests for the workout authoring cluster, aligned to the canonical schema
(TASK-0023/0033/0035/0025/0050/0024/0063)."""

from __future__ import annotations

import json

import pytest

from yourtrainer_mcp import workout as wk

INTENT = {
    "name": "Sweet Spot 2x20",
    "description": "Classic sweet-spot session",
    "workout_type": "POWER",
    "category": "sweet-spot",
    "difficulty": 3,
    "warmup": {"duration_seconds": 600, "zone": "Z2", "label": "Warmup", "id": "warmup",
               "target_power_percent": 50, "target_power_end_percent": 75,
               "cues": [{"offset_seconds": 0, "text": "Spin up"}]},
    "intervals": [
        {"duration_seconds": 1200, "zone": "Z3", "label": "Sweet Spot", "id": "ss",
         "target_power_percent": 90, "cadence_target": 90},
        {"duration_seconds": 300, "zone": "Z1", "label": "Recovery", "id": "rec",
         "target_power_percent": 50},
        {"repeat": 4, "intervals": [
            {"duration_seconds": 60, "zone": "Z5", "label": "On", "id": "on",
             "target_power_percent": 120},
            {"duration_seconds": 60, "zone": "Z1", "label": "Off", "id": "off",
             "target_power_percent": 50}]},
    ],
    "cooldown": {"duration_seconds": 600, "zone": "Z1", "label": "Cooldown", "id": "cooldown",
                 "target_power_percent": 60, "target_power_end_percent": 40},
}


def test_build_and_total_duration():
    w = wk.build_workout(INTENT)
    # 600 + 1200 + 300 + 4*(60+60) + 600 = 3180; warmup + 3 items + cooldown = 5 intervals
    assert w.total_duration_s() == 3180
    assert len(w.intervals) == 5
    assert w.name == "Sweet Spot 2x20"


def test_build_rejects_missing_fields():
    with pytest.raises(wk.WorkoutError):
        wk.build_workout({"name": "x", "description": "d", "intervals": [],
                          "cooldown": {"duration_seconds": 1, "zone": "Z1", "label": "c",
                                       "target_power_percent": 50}})  # no warmup
    with pytest.raises(wk.WorkoutError):
        # warmup block missing target_power_percent for a POWER workout
        wk.build_workout({"name": "x", "description": "d",
                          "warmup": {"duration_seconds": 60, "zone": "Z1", "label": "w"},
                          "intervals": [], "cooldown": {"duration_seconds": 60, "zone": "Z1",
                                                        "label": "c", "target_power_percent": 50}})


def test_ytw_matches_canonical_shape():
    w = wk.build_workout(INTENT)
    doc = json.loads(wk.to_ytw(w))
    assert doc["programId"] == "sweet-spot-2x20"
    assert doc["programName"] == "Sweet Spot 2x20"
    assert doc["workoutType"] == "POWER"
    assert doc["totalDuration"] == 3180
    # warmup carries intervalType + ramp end; repeat group preserved
    assert doc["intervals"][0]["intervalType"] == "WARMUP"
    assert doc["intervals"][0]["targetPowerEndPercent"] == 75
    assert doc["intervals"][3]["repeat"] == 4
    assert doc["strings"]["en"]["labels"]["ss"] == "Sweet Spot"
    assert doc["strings"]["en"]["cues"]["warmup:0"] == "Spin up"


def test_zwo_roundtrip_preserves_power_series():
    w = wk.build_workout(INTENT)
    zwo = wk.to_zwo(w)
    assert "<workout_file>" in zwo and "IntervalsT" in zwo
    back = wk.from_zwo(zwo)
    assert wk.expand_to_power_series(w, 250.0) == wk.expand_to_power_series(back, 250.0)


def test_ytw_roundtrip_preserves_power_series():
    w = wk.build_workout(INTENT)
    back = wk.from_ytw(wk.to_ytw(w))
    assert back.total_duration_s() == w.total_duration_s()
    assert wk.expand_to_power_series(w, 250.0) == wk.expand_to_power_series(back, 250.0)


def test_from_ytw_rejects_non_ytw():
    with pytest.raises(wk.WorkoutError):
        wk.from_ytw(json.dumps({"format": "nope"}))


def test_scale_duration_halves():
    w = wk.build_workout(INTENT)
    half = wk.scale_workout(w, duration_factor=0.5)
    assert half.total_duration_s() == pytest.approx(w.total_duration_s() / 2, abs=6)
    assert "50% duration" in half.name


def test_scale_intensity_raises_power():
    w = wk.build_workout(INTENT)
    harder = wk.scale_workout(w, intensity_factor=1.1)
    assert harder.total_duration_s() == w.total_duration_s()
    ss = harder.intervals[1]  # the Z3 sweet-spot block (90 -> 99)
    assert ss.target_power_percent == 99


def test_scale_rejects_non_positive():
    with pytest.raises(wk.WorkoutError):
        wk.scale_workout(wk.build_workout(INTENT), duration_factor=0)


def test_difficulty_is_ftp_independent():
    w = wk.build_workout(INTENT)
    score = wk.difficulty_score(w, ftp=250.0)
    assert score["duration_s"] == 3180
    assert 0 < score["intensity_factor"] < 1.2 and score["tss"] > 0
    assert score["tss"] == pytest.approx(wk.difficulty_score(w, ftp=300.0)["tss"], abs=0.1)


def test_lint_flags_missing_warmup_and_zero_duration():
    bad = wk.Workout(name="", intervals=[
        wk.Block(duration_seconds=0, zone="Z3", label="x", target_power_percent=80)])
    codes = {f["code"] for f in wk.lint_workout(bad)}
    assert {"zero-duration", "no-warmup", "no-name"} <= codes


def test_lint_clean_workout_has_no_errors():
    findings = wk.lint_workout(wk.build_workout(INTENT))
    assert not [f for f in findings if f["severity"] == "error"]


def test_lint_flags_implausible_power():
    w = wk.Workout(name="x", intervals=[
        wk.Block(60, "Z1", "Warm Up", interval_type="WARMUP", target_power_percent=40),
        wk.Block(60, "Z7", "x", target_power_percent=900)])
    assert "power-range" in {f["code"] for f in wk.lint_workout(w)}


# ---- app-acceptance (verified, sourced) ----

def test_app_acceptance_garmin_step_limit():
    blocks = [wk.Block(60, "Z3", "w", target_power_percent=80) for _ in range(60)]
    result = wk.app_acceptance(wk.Workout(name="x", intervals=blocks), apps=["garmin"])
    assert result["garmin"]["accepted"] is False
    assert any("50-step" in i for i in result["garmin"]["issues"])


def test_app_acceptance_garmin_warns_on_ramp_expansion():
    w = wk.Workout(name="x", intervals=[
        wk.Block(60, "Z2", "Warm Up", interval_type="WARMUP", target_power_percent=40,
                 target_power_end_percent=70),
        wk.Block(60, "Z3", "Work", target_power_percent=80)])
    result = wk.app_acceptance(w, apps=["garmin"])
    assert result["garmin"]["accepted"] is True
    assert any("ramp" in w_.lower() for w_ in result["garmin"]["warnings"])


def test_app_acceptance_garmin_repeat_limit():
    w = wk.Workout(name="x", intervals=[wk.Repeat(repeat=120, intervals=[
        wk.Block(30, "Z5", "On", target_power_percent=120),
        wk.Block(30, "Z1", "Off", target_power_percent=50)])])
    result = wk.app_acceptance(w, apps=["garmin"])
    assert result["garmin"]["accepted"] is False
    assert any("repeat" in i for i in result["garmin"]["issues"])


def test_app_acceptance_zwift_accepts_ramp():
    result = wk.app_acceptance(wk.build_workout(INTENT), apps=["zwift"])
    assert result["zwift"]["accepted"] is True


def test_app_acceptance_unknown_app_is_indeterminate():
    result = wk.app_acceptance(wk.build_workout(INTENT), apps=["peloton"])
    assert result["peloton"]["accepted"] is None
