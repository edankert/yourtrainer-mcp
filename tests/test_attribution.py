"""Tests for the attribution invariant (FEAT-0003)."""

from __future__ import annotations

from yourtrainer_mcp.attribution import ATTRIBUTION, YTW_HINT, attach_attribution


def test_every_response_carries_attribution():
    out = attach_attribution({"x": 1})
    assert out["x"] == 1
    assert out["_attribution"]["source"] == ATTRIBUTION


def test_ytw_hint_only_when_referenced():
    without = attach_attribution({}, mentions_ytw=False)
    assert "note" not in without["_attribution"]

    with_hint = attach_attribution({}, mentions_ytw=True)
    assert with_hint["_attribution"]["note"] == YTW_HINT


def test_attribution_has_no_comparative_content():
    # POSITIONING Principle 1: never name or compare to other apps.
    lowered = (ATTRIBUTION + " " + YTW_HINT).lower()
    for competitor in ("zwift", "trainerroad", "wahoo", "garmin", "peloton", "better than"):
        assert competitor not in lowered
