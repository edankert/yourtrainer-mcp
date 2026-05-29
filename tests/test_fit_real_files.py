"""Validation against real-world FIT files (TASK-0020).

Fixtures are MIT-licensed files from python-fitparse (see
tests/fixtures/external/NOTICE.md). These exercise the FIT reader on genuine
Garmin output — activity and workout files — not just our own encoder.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from yourtrainer_mcp import fit, fit_workout
from yourtrainer_mcp import power as pw
from yourtrainer_mcp.activity import inspect_activity, parse_activity_file

EXT = Path(__file__).parent / "fixtures" / "external"
EDGE810 = EXT / "Edge810-Vector-2013-08-16-15-35-10.fit"


def test_reads_real_activity_file():
    msgs = fit.decode((EXT / "Activity.fit").read_bytes())
    globals_ = {g for g, _ in msgs}
    assert 0 in globals_  # file_id
    assert 20 in globals_  # record


@pytest.mark.parametrize("name,min_steps", [
    ("WorkoutIndividualSteps.fit", 3),
    ("WorkoutRepeatSteps.fit", 3),
    ("WorkoutCustomTargetValues.fit", 3),
])
def test_reads_real_garmin_workout_files(name, min_steps):
    w = fit_workout.decode_workout_fit((EXT / name).read_bytes())
    assert w.name  # workout name decoded
    assert len(w.intervals) >= min_steps
    assert all(b.interval_type in {"WARMUP", "COOLDOWN", "INTERVAL"} for b in w.intervals)


def test_real_ride_power_metrics_are_plausible():
    samples = fit.decode_activity(EDGE810.read_bytes())
    power = [s["power"] for s in samples if "power" in s]
    assert len(power) == 4700
    np = pw.normalized_power(power)
    assert np > pw.average(power)        # variable ride
    assert 295 < np < 305                # cross-validated ~301 W


def test_builtin_and_fitparse_agree_on_real_ride():
    # The built-in parser (CI default) and fitparse (optional extra) must read
    # the same power stream. Skips cleanly when fitparse isn't installed.
    fitparse = pytest.importorskip("fitparse")
    builtin = [s["power"] for s in fit.decode_activity(EDGE810.read_bytes()) if "power" in s]
    ff = fitparse.FitFile(str(EDGE810))
    fp = [float({d.name: d.value for d in r}.get("power"))
          for r in ff.get_messages("record")
          if {d.name: d.value for d in r}.get("power") is not None]
    assert len(builtin) == len(fp)
    assert pw.normalized_power(builtin) == pytest.approx(pw.normalized_power(fp), abs=0.05)


def test_inspect_real_ride_end_to_end():
    summary = inspect_activity(parse_activity_file(EDGE810), ftp=275.0)
    p = summary["power"]
    assert p["normalized_power_w"] == pytest.approx(301.1, abs=0.5)
    assert p["intensity_factor"] == pytest.approx(1.095, abs=0.01)
    assert p["training_stress_score"] == pytest.approx(156.5, abs=1.0)


def test_real_hr_only_ride_has_no_phantom_power():
    # Edge 500 with no power meter: FIT records power == 0xFFFF (invalid). The
    # sentinel must be dropped, not read as 65535 W. HR is present.
    f = EXT / "garmin-edge-500-activity.fit"
    samples = fit.decode_activity(f.read_bytes())
    assert not [s for s in samples if "power" in s]
    assert sum(1 for s in samples if "heart_rate" in s) > 1000
    summary = inspect_activity(parse_activity_file(f), 250.0)
    assert summary["power"] is None
    assert summary["heart_rate"]["avg_bpm"] > 0
