"""Tests for the Your Trainer content client + tools (FEAT-0007).

Hermetic: a local-fixture fetcher is injected, so no network is touched.
Fixtures under tests/fixtures/website/ are first-party Your Trainer content.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from yourtrainer_mcp import content

WEB = Path(__file__).parent / "fixtures" / "website"


def _local_fetch(url: str) -> str:
    # url is "<base>/<path>"; map the path onto the fixtures dir.
    path = url.split("/your-trainer/", 1)[1] if "/your-trainer/" in url else url
    return (WEB / path).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _use_fixtures():
    content.set_base_url("https://www.your-applications.com/your-trainer")
    content.set_fetcher(_local_fetch)
    yield
    content.clear_cache()


# ---- workout library ----

def test_list_workouts_and_filter():
    allw = content.list_workouts()
    assert len(allw) == 26
    assert all("ytw" not in w for w in allw)  # list returns metadata only
    short = content.list_workouts(max_duration_s=3600)
    assert all(w["duration_seconds"] <= 3600 for w in short)
    assert all(w["set"] == "power" for w in content.list_workouts(set_="power"))


def test_get_workout_includes_ytw_body():
    w = content.get_workout("sweet-spot-3x10min-at-88pct-ftp")
    assert w["name"].startswith("Sweet Spot")
    # Real Your Trainer .ytw uses programId/programName (see ISS-0001: our
    # build_workout .ytw writer uses a simpler schema and needs reconciling).
    assert w["ytw"] and ("programId" in w["ytw"] or "programName" in w["ytw"])


def test_get_workout_unknown_raises():
    with pytest.raises(KeyError):
        content.get_workout("does-not-exist")


def test_search_workouts():
    res = content.search_workouts("sweet spot")
    assert res and all("name" in w for w in res)


def test_caching_avoids_refetch(monkeypatch):
    calls = {"n": 0}

    def counting(url):
        calls["n"] += 1
        return _local_fetch(url)

    content.set_fetcher(counting)
    content.library_manifest()
    content.library_manifest()
    assert calls["n"] == 1  # second call served from cache


# ---- manual ----

def test_manual_sections_parsed():
    secs = content.manual_sections()
    titles = [s["title"] for s in secs]
    assert any("Workout library" in t for t in titles)
    assert all(s["key"] for s in secs)


def test_search_manual_returns_snippets():
    res = content.search_manual("workout")
    assert res and "snippet" in res[0] and "title" in res[0]


def test_get_manual_section_roundtrip():
    secs = content.manual_sections()
    key = secs[1]["key"]
    got = content.get_manual_section(key)
    assert got["key"] == key and got["text"]


# ---- ai skills ----

def test_ai_skills_listed():
    skills = content.ai_skills()
    assert len(skills) >= 3
    titles = [s["title"].lower() for s in skills]
    assert any("prompt" in t or "pattern" in t or "coach" in t for t in titles)
    assert "on this page" not in titles
