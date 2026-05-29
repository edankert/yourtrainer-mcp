"""Property-based tests (TASK-0041).

Hypothesis strategies generate arbitrary-but-valid workouts and power series to
assert invariants that must hold for *all* inputs, not just hand-picked cases.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from yourtrainer_mcp import fit_workout
from yourtrainer_mcp import power as pw
from yourtrainer_mcp import workout as wk

# ---- strategies ----

# Realistic FTP fractions: 2 decimal places (0.30–1.60). Workouts are authored
# at this precision, and both ZWO (%g) and FIT (%FTP integer) preserve it
# exactly, so format roundtrips are genuinely lossless for such inputs.
_frac = st.integers(min_value=30, max_value=160).map(lambda x: x / 100)
_dur = st.integers(min_value=5, max_value=400)


@st.composite
def _step(draw):
    kind = draw(st.sampled_from(["warmup", "cooldown", "steady", "ramp", "interval"]))
    if kind == "interval":
        return {"kind": "interval", "repeat": draw(st.integers(1, 6)),
                "on_duration_s": draw(_dur), "off_duration_s": draw(_dur),
                "on_power": draw(_frac), "off_power": draw(_frac)}
    if kind == "steady":
        return {"kind": "steady", "duration_s": draw(_dur), "power": draw(_frac)}
    return {"kind": kind, "duration_s": draw(_dur),
            "power_low": draw(_frac), "power_high": draw(_frac)}


@st.composite
def _intent(draw):
    steps = draw(st.lists(_step(), min_size=1, max_size=6))
    return {"name": "P", "steps": steps}


# ---- power-math invariants ----

@given(st.lists(st.floats(min_value=0, max_value=2000, allow_nan=False), min_size=1, max_size=500))
def test_np_never_below_average(power):
    # NP is a 4th-power mean of a smoothed series; it can only meet or exceed
    # the arithmetic mean.
    assert pw.normalized_power(power) >= pw.average(power) - 1e-6


@given(st.floats(min_value=1, max_value=600), st.integers(min_value=1, max_value=600))
def test_constant_power_np_equals_value(value, n):
    # (v**4)**0.25 is not bit-exact for all floats, hence approx.
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
    # Each rounded duration adds ≤1 s of error; intervals round per on/off block
    # and that error is multiplied by the repeat count in the total.
    slack = 1
    for s in w.steps:
        slack += (s.repeat or 1) if s.kind == "interval" else 1
    assert abs(scaled.total_duration_s() - expected) <= slack


@settings(max_examples=80, deadline=None)
@given(_intent())
def test_fit_roundtrip_preserves_power_series_within_quantisation(intent):
    w = wk.build_workout(intent)
    back = fit_workout.decode_workout_fit(fit_workout.encode_workout_fit(w))
    s1 = wk.expand_to_power_series(w, 250.0)
    s2 = wk.expand_to_power_series(back, 250.0)
    assert len(s1) == len(s2)
    # FIT %FTP integer quantisation: ≤0.5% FTP == 1.25 W at FTP 250.
    assert all(abs(a - b) <= 1.25 for a, b in zip(s1, s2, strict=True))
