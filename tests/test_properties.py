"""Property-based tests (TASK-0041), aligned to the canonical schema.

Hypothesis generates arbitrary-but-valid workout intents and power series to
assert invariants that must hold for *all* inputs.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from yourtrainer_mcp import fit_workout
from yourtrainer_mcp import power as pw
from yourtrainer_mcp import workout as wk

# Realistic integer FTP percentages (30–160%).
_pct = st.integers(min_value=30, max_value=160)
_dur = st.integers(min_value=5, max_value=400)
_zone = st.sampled_from(["Z1", "Z2", "Z3", "Z4", "Z5"])


@st.composite
def _block(draw, label="Work"):
    b = {"duration_seconds": draw(_dur), "zone": draw(_zone), "label": label,
         "target_power_percent": draw(_pct)}
    if draw(st.booleans()):
        b["target_power_end_percent"] = draw(_pct)  # ramp
    return b


@st.composite
def _middle(draw):
    if draw(st.booleans()):
        return {"repeat": draw(st.integers(1, 6)),
                "intervals": draw(st.lists(_block(), min_size=1, max_size=3))}
    return draw(_block())


@st.composite
def _intent(draw):
    return {
        "name": "P", "description": "d", "workout_type": "POWER",
        "warmup": {"duration_seconds": draw(_dur), "zone": "Z2", "label": "Warmup",
                   "target_power_percent": draw(_pct), "target_power_end_percent": draw(_pct)},
        "intervals": draw(st.lists(_middle(), min_size=1, max_size=5)),
        "cooldown": {"duration_seconds": draw(_dur), "zone": "Z1", "label": "Cooldown",
                     "target_power_percent": draw(_pct), "target_power_end_percent": draw(_pct)},
    }


def _expanded_block_count(w: wk.Workout) -> int:
    n = 0
    for it in w.intervals:
        n += it.repeat * len(it.intervals) if isinstance(it, wk.Repeat) else 1
    return n


# ---- power-math invariants ----

@given(st.lists(st.floats(min_value=0, max_value=2000, allow_nan=False), min_size=1, max_size=500))
def test_np_is_quartic_mean_of_rolling(power):
    rolling = pw.rolling_average(power, 30)
    assert pw.normalized_power(power) >= pw.average(rolling) - 1e-6


@given(st.floats(min_value=1, max_value=600), st.integers(min_value=1, max_value=600))
def test_constant_power_np_equals_value(value, n):
    assert pw.normalized_power([value] * n) == pytest.approx(value, rel=1e-9)


# ---- workout roundtrip invariants ----

@settings(max_examples=150, deadline=None)
@given(_intent())
def test_zwo_roundtrip_preserves_power_series(intent):
    w = wk.build_workout(intent)
    back = wk.from_zwo(wk.to_zwo(w))
    assert wk.expand_to_power_series(w, 250.0) == wk.expand_to_power_series(back, 250.0)


@settings(max_examples=150, deadline=None)
@given(_intent())
def test_ytw_roundtrip_preserves_power_series(intent):
    w = wk.build_workout(intent)
    back = wk.from_ytw(wk.to_ytw(w))
    assert wk.expand_to_power_series(w, 250.0) == wk.expand_to_power_series(back, 250.0)


@settings(max_examples=100, deadline=None)
@given(_intent())
def test_difficulty_is_ftp_independent(intent):
    w = wk.build_workout(intent)
    assert wk.difficulty_score(w, 200.0)["tss"] == wk.difficulty_score(w, 330.0)["tss"]


@settings(max_examples=100, deadline=None)
@given(_intent(), st.floats(min_value=0.25, max_value=3.0))
def test_scale_duration_is_proportional(intent, factor):
    w = wk.build_workout(intent)
    scaled = wk.scale_workout(w, duration_factor=factor)
    expected = w.total_duration_s() * factor
    # Each expanded block's duration is rounded independently (≤1 s each).
    slack = _expanded_block_count(w) + 1
    assert abs(scaled.total_duration_s() - expected) <= slack


@settings(max_examples=80, deadline=None)
@given(_intent())
def test_fit_roundtrip_is_exact(intent):
    w = wk.build_workout(intent)
    back = fit_workout.decode_workout_fit(fit_workout.encode_workout_fit(w))
    # Integer %FTP -> the per-second power series round-trips exactly.
    assert wk.expand_to_power_series(w, 250.0) == wk.expand_to_power_series(back, 250.0)
