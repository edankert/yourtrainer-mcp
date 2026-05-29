"""Reference-value corpus for NP/IF/TSS (TASK-0045).

Validates the power engine against (a) synthetic analytic anchors with exact
known values (the TrainingPeaks 1h-at-FTP = 100 TSS anchor and friends) and
(b) a real ride whose NP is cross-validated three ways. Values live in
tests/fixtures/reference_values.json so the corpus is data-driven and grows by
adding entries, not code.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from yourtrainer_mcp import fit
from yourtrainer_mcp import power as pw

FIX = Path(__file__).parent / "fixtures"
CORPUS = json.loads((FIX / "reference_values.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("a", CORPUS["anchors"], ids=lambda a: a["id"])
def test_synthetic_anchors(a):
    power = [float(a["constant_power"])] * a["duration_s"]
    np = pw.normalized_power(power)
    if_ = pw.intensity_factor(np, a["ftp"])
    tss = pw.training_stress_score(a["duration_s"], np, a["ftp"])
    assert np == pytest.approx(a["expected"]["np"], abs=0.01)
    assert if_ == pytest.approx(a["expected"]["if"], abs=0.001)
    assert tss == pytest.approx(a["expected"]["tss"], abs=0.05)


@pytest.mark.parametrize("act", CORPUS["real_activities"], ids=lambda a: a["id"])
def test_real_activity_reference_values(act):
    data = (FIX / act["file"]).read_bytes()
    power = [s["power"] for s in fit.decode_activity(data) if "power" in s]
    assert len(power) == act["duration_s"]
    np = pw.normalized_power(power)
    if_ = pw.intensity_factor(np, act["ftp"])
    tss = pw.training_stress_score(len(power), np, act["ftp"])
    tol = act["tolerance"]
    assert np == pytest.approx(act["expected"]["np"], abs=tol["np"])
    assert if_ == pytest.approx(act["expected"]["if"], abs=tol["if"])
    assert tss == pytest.approx(act["expected"]["tss"], abs=tol["tss"])


def test_np_matches_independent_naive_implementation():
    # Guards the optimized sliding-window NP against an O(n*w) reference.
    data = (FIX / "external" / "Edge810-Vector-2013-08-16-15-35-10.fit").read_bytes()
    power = [s["power"] for s in fit.decode_activity(data) if "power" in s]

    def naive_np(p, w=30):
        if len(p) < w:
            return pw.average(p)
        roll = [sum(p[i - w + 1:i + 1]) / w for i in range(w - 1, len(p))]
        return (sum(r ** 4 for r in roll) / len(roll)) ** 0.25

    assert pw.normalized_power(power) == pytest.approx(naive_np(power), abs=1e-6)
