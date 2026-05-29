"""≥10 FIT-workout sample corpus (TASK-0020).

Combines the three real Garmin workout files with a diverse set of generated
workouts (canonical-schema intents). Each generated workout is encoded to FIT,
decoded back (power profile preserved — integer %FTP round-trips exactly), and,
when fitparse is present, independently re-parsed to confirm valid FIT bytes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from yourtrainer_mcp import fit_workout
from yourtrainer_mcp import workout as wk

EXT = Path(__file__).parent / "fixtures" / "external"
REAL_WORKOUTS = ["WorkoutIndividualSteps.fit", "WorkoutRepeatSteps.fit",
                 "WorkoutCustomTargetValues.fit"]


def _wu(lo=40, hi=70, dur=600):
    return {"duration_seconds": dur, "zone": "Z2", "label": "Warmup",
            "target_power_percent": lo, "target_power_end_percent": hi}


def _cd(lo=60, hi=40, dur=300):
    return {"duration_seconds": dur, "zone": "Z1", "label": "Cooldown",
            "target_power_percent": lo, "target_power_end_percent": hi}


def _blk(dur, pct, zone="Z3", label="Work", end=None):
    b = {"duration_seconds": dur, "zone": zone, "label": label, "target_power_percent": pct}
    if end is not None:
        b["target_power_end_percent"] = end
    return b


def _intent(name, intervals):
    return {"name": name, "description": name, "workout_type": "POWER",
            "warmup": _wu(), "intervals": intervals, "cooldown": _cd()}


GENERATED = [
    _intent("Recovery", [_blk(1800, 50, "Z1", "Easy")]),
    _intent("Endurance", [_blk(5400, 65, "Z2", "Endurance")]),
    _intent("Sweet Spot 3x12", [{"repeat": 3, "intervals": [
        _blk(720, 90, "Z3", "Sweet Spot"), _blk(300, 55, "Z1", "Recovery")]}]),
    _intent("Threshold 2x20", [{"repeat": 2, "intervals": [
        _blk(1200, 100, "Z4", "Threshold"), _blk(300, 50, "Z1", "Recovery")]}]),
    _intent("VO2 5x3", [{"repeat": 5, "intervals": [
        _blk(180, 115, "Z5", "VO2"), _blk(180, 50, "Z1", "Recovery")]}]),
    _intent("Anaerobic 8x30", [{"repeat": 8, "intervals": [
        _blk(30, 150, "Z6", "Sprint"), _blk(150, 45, "Z1", "Recovery")]}]),
    _intent("Ramp", [_blk(1500, 50, "Z2", "Ramp", end=120)]),
    _intent("Over-Unders", [{"repeat": 6, "intervals": [
        _blk(120, 105, "Z4", "Over"), _blk(120, 88, "Z3", "Under")]}]),
    _intent("Tempo", [_blk(1800, 80, "Z3", "Tempo")]),
    _intent("Pyramid", [_blk(60, 90), _blk(120, 100), _blk(180, 110, "Z5"),
                        _blk(120, 100), _blk(60, 90)]),
]


def test_corpus_has_at_least_ten_samples():
    assert len(GENERATED) + len(REAL_WORKOUTS) >= 10


@pytest.mark.parametrize("intent", GENERATED, ids=[w["name"] for w in GENERATED])
def test_generated_workout_fit_roundtrips(intent):
    w = wk.build_workout(intent)
    data = fit_workout.encode_workout_fit(w)
    assert data[8:12] == b".FIT"
    back = fit_workout.decode_workout_fit(data)
    s1 = wk.expand_to_power_series(w, 250.0)
    s2 = wk.expand_to_power_series(back, 250.0)
    assert len(s1) == len(s2)
    assert s1 == s2  # integer %FTP -> exact round-trip


@pytest.mark.parametrize("intent", GENERATED, ids=[w["name"] for w in GENERATED])
def test_generated_workout_parses_in_fitparse(intent):
    fitparse = pytest.importorskip("fitparse")
    import io
    data = fit_workout.encode_workout_fit(wk.build_workout(intent))
    ff = fitparse.FitFile(io.BytesIO(data))
    assert len(list(ff.get_messages("workout_step"))) >= 1


@pytest.mark.parametrize("name", REAL_WORKOUTS)
def test_real_workout_decodes(name):
    w = fit_workout.decode_workout_fit((EXT / name).read_bytes())
    assert w.name and len(w.intervals) >= 3
