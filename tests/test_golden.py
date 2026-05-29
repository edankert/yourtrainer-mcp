"""Golden-file regression tests (TASK-0041).

Locks the exact rendered output of a canonical workout. If a refactor changes
ZWO/.ytw serialisation or the difficulty math, these fail loudly. Regenerate
intentionally via scripts in the commit that changes the format.
"""

from __future__ import annotations

import json
from pathlib import Path

from yourtrainer_mcp import workout as wk

GOLDEN = Path(__file__).parent / "golden"


def _read(name: str) -> str:
    return (GOLDEN / name).read_text(encoding="utf-8")


def _canon() -> wk.Workout:
    intent = json.loads(_read("sweet_spot.intent.json"))
    return wk.build_workout(intent)


def test_zwo_matches_golden():
    assert wk.to_zwo(_canon()) == _read("sweet_spot.zwo")


def test_ytw_matches_golden():
    assert wk.to_ytw(_canon()) + "\n" == _read("sweet_spot.ytw")


def test_difficulty_matches_golden():
    got = wk.difficulty_score(_canon(), 250.0)
    expected = json.loads(_read("sweet_spot.difficulty.json"))
    assert got == expected


def test_golden_zwo_still_parses_back():
    # The golden artefact must remain a valid, decodable workout.
    back = wk.from_zwo(_read("sweet_spot.zwo"))
    assert back.total_duration_s() == _canon().total_duration_s()
