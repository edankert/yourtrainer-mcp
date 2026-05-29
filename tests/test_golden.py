"""Golden-file regression tests (TASK-0041).

Locks the exact rendered output of a canonical workout against the committed
.ytw / .zwo / difficulty fixtures. If a refactor changes serialisation or the
difficulty math, these fail loudly. Regenerate intentionally in the commit that
changes the format.
"""

from __future__ import annotations

import json
from pathlib import Path

from yourtrainer_mcp import workout as wk

GOLDEN = Path(__file__).parent / "golden"


def _read(name: str) -> str:
    return (GOLDEN / name).read_text(encoding="utf-8")


def _canon() -> wk.Workout:
    return wk.build_workout(json.loads(_read("sweet_spot.intent.json")))


def test_ytw_matches_golden():
    assert wk.to_ytw(_canon()) + "\n" == _read("sweet_spot.ytw")


def test_zwo_matches_golden():
    assert wk.to_zwo(_canon()) == _read("sweet_spot.zwo")


def test_difficulty_matches_golden():
    got = wk.difficulty_score(_canon(), 250.0)
    assert got == json.loads(_read("sweet_spot.difficulty.json"))


def test_golden_ytw_is_canonical_shape():
    doc = json.loads(wk.to_ytw(_canon()))
    assert {"programId", "programName", "totalDuration", "intervals"} <= doc.keys()
    back = wk.from_ytw(_read("sweet_spot.ytw"))
    assert back.total_duration_s() == _canon().total_duration_s()
