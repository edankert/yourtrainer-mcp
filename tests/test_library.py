"""Tests for library-aware operations (FEAT-0006)."""

from __future__ import annotations

from yourtrainer_mcp import fit, library
from yourtrainer_mcp import workout as wk


def _write_workout(tmp_path, name, intent, fmt="ytw"):
    w = wk.build_workout(intent)
    doc = wk.to_ytw(w) if fmt == "ytw" else wk.to_zwo(w)
    p = tmp_path / f"{name}.{fmt}"
    p.write_text(doc, encoding="utf-8")
    return str(p)


SS = {"name": "SS", "steps": [{"kind": "steady", "duration_s": 1200, "power": 0.88}]}
EASY = {"name": "Easy", "steps": [{"kind": "steady", "duration_s": 1800, "power": 0.55}]}


def test_index_library_mixes_workouts_and_activities(tmp_path):
    w1 = _write_workout(tmp_path, "ss", SS, "ytw")
    w2 = _write_workout(tmp_path, "easy", EASY, "zwo")
    act = tmp_path / "ride.fit"
    act.write_bytes(fit.encode_activity_fit([{"power": 200} for _ in range(600)]))
    idx = library.index_library([w1, w2, str(act)], ftp_watts=250.0)
    assert idx["count"] == 3
    kinds = {e["kind"] for e in idx["entries"]}
    assert kinds == {"workout", "activity"}


def test_find_duplicates_groups_identical_workouts(tmp_path):
    a = _write_workout(tmp_path, "a", SS, "ytw")
    b = _write_workout(tmp_path, "b", SS, "zwo")  # same profile, different format
    c = _write_workout(tmp_path, "c", EASY, "ytw")
    out = library.find_duplicates([a, b, c], ftp_watts=250.0)
    assert out["group_count"] == 1
    assert {"a.ytw", "b.zwo"} == set(out["duplicate_groups"][0])


def test_library_stats_aggregates(tmp_path):
    a = _write_workout(tmp_path, "a", SS, "ytw")
    c = _write_workout(tmp_path, "c", EASY, "ytw")
    stats = library.library_stats([a, c], ftp_watts=250.0)
    assert stats["files_indexed"] == 2
    assert stats["by_kind"]["workout"] == 2
    assert stats["total_duration_s"] == 3000  # 1200 + 1800
    assert stats["total_tss"] > 0


def test_best_efforts_across_history(tmp_path):
    a = tmp_path / "a.fit"
    a.write_bytes(fit.encode_activity_fit([{"power": 200} for _ in range(120)]))
    b = tmp_path / "b.fit"
    b.write_bytes(fit.encode_activity_fit([{"power": 350} for _ in range(120)]))
    out = library.best_efforts_across_history([str(a), str(b)])
    # The 5 s best should come from the higher-power file.
    assert out["best_efforts"]["5"]["watts"] == 350.0
    assert out["best_efforts"]["5"]["file"] == "b.fit"
