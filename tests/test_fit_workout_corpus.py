"""≥10 FIT-workout sample corpus (TASK-0020).

Combines the three real Garmin workout files with a diverse set of generated
workouts. Each generated workout is encoded to FIT, decoded back (power profile
preserved within %FTP quantisation), and — when the optional fitparse extra is
present — independently re-parsed to confirm the bytes are valid FIT.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from yourtrainer_mcp import fit_workout
from yourtrainer_mcp import workout as wk

EXT = Path(__file__).parent / "fixtures" / "external"
REAL_WORKOUTS = ["WorkoutIndividualSteps.fit", "WorkoutRepeatSteps.fit",
                 "WorkoutCustomTargetValues.fit"]

# 10 diverse synthetic-but-realistic workouts covering every step kind/combo.
GENERATED = [
    {"name": "Recovery", "steps": [{"kind": "steady", "duration_s": 1800, "power": 0.5}]},
    {"name": "Endurance", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.6},
        {"kind": "steady", "duration_s": 5400, "power": 0.65},
        {"kind": "cooldown", "duration_s": 600, "power_low": 0.6, "power_high": 0.4}]},
    {"name": "Sweet Spot 3x12", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.45, "power_high": 0.75},
        {"kind": "interval", "repeat": 3, "on_duration_s": 720, "off_duration_s": 300,
         "on_power": 0.9, "off_power": 0.55},
        {"kind": "cooldown", "duration_s": 420, "power_low": 0.6, "power_high": 0.4}]},
    {"name": "Threshold 2x20", "steps": [
        {"kind": "warmup", "duration_s": 900, "power_low": 0.4, "power_high": 0.8},
        {"kind": "interval", "repeat": 2, "on_duration_s": 1200, "off_duration_s": 300,
         "on_power": 1.0, "off_power": 0.5}]},
    {"name": "VO2 5x3", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.8},
        {"kind": "interval", "repeat": 5, "on_duration_s": 180, "off_duration_s": 180,
         "on_power": 1.15, "off_power": 0.5},
        {"kind": "cooldown", "duration_s": 300, "power_low": 0.6, "power_high": 0.4}]},
    {"name": "Anaerobic 8x30", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.85},
        {"kind": "interval", "repeat": 8, "on_duration_s": 30, "off_duration_s": 150,
         "on_power": 1.5, "off_power": 0.45}]},
    {"name": "Ramp Test", "steps": [
        {"kind": "ramp", "duration_s": 1500, "power_low": 0.4, "power_high": 1.5}]},
    {"name": "Over-Unders", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.8},
        {"kind": "interval", "repeat": 6, "on_duration_s": 120, "off_duration_s": 120,
         "on_power": 1.05, "off_power": 0.88},
        {"kind": "cooldown", "duration_s": 300, "power_low": 0.6, "power_high": 0.4}]},
    {"name": "Free Ride Opener", "steps": [
        {"kind": "warmup", "duration_s": 300, "power_low": 0.4, "power_high": 0.7},
        {"kind": "freeride", "duration_s": 1200},
        {"kind": "steady", "duration_s": 300, "power": 0.55}]},
    {"name": "Pyramid", "steps": [
        {"kind": "warmup", "duration_s": 600, "power_low": 0.4, "power_high": 0.75},
        {"kind": "steady", "duration_s": 60, "power": 0.9},
        {"kind": "steady", "duration_s": 120, "power": 1.0},
        {"kind": "steady", "duration_s": 180, "power": 1.1},
        {"kind": "steady", "duration_s": 120, "power": 1.0},
        {"kind": "steady", "duration_s": 60, "power": 0.9},
        {"kind": "cooldown", "duration_s": 300, "power_low": 0.6, "power_high": 0.4}]},
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
    assert all(abs(a - b) <= 1.25 for a, b in zip(s1, s2, strict=True))


@pytest.mark.parametrize("intent", GENERATED, ids=[w["name"] for w in GENERATED])
def test_generated_workout_parses_in_fitparse(intent):
    fitparse = pytest.importorskip("fitparse")
    import io
    data = fit_workout.encode_workout_fit(wk.build_workout(intent))
    ff = fitparse.FitFile(io.BytesIO(data))
    steps = list(ff.get_messages("workout_step"))
    assert len(steps) >= 1  # an independent parser accepts our bytes


@pytest.mark.parametrize("name", REAL_WORKOUTS)
def test_real_workout_decodes(name):
    w = fit_workout.decode_workout_fit((EXT / name).read_bytes())
    assert w.name and len(w.steps) >= 3
