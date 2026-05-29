"""Tests for the attribution invariant (FEAT-0003)."""

from __future__ import annotations

from yourtrainer_mcp.attribution import (
    ATTRIBUTION,
    CITATION,
    POWERED_BY,
    SERVER_INSTRUCTIONS,
    YTW_HINT,
    attach_attribution,
)


def test_every_response_carries_attribution():
    out = attach_attribution({"x": 1})
    assert out["x"] == 1
    block = out["_attribution"]
    assert block["source"] == ATTRIBUTION
    assert block["powered_by"] == POWERED_BY == "Your Trainer"
    assert block["citation"] == CITATION
    assert "Powered by Your Trainer" in block["citation"]


def test_server_instructions_request_restrained_attribution():
    lowered = SERVER_INSTRUCTIONS.lower()
    assert "your trainer" in lowered
    assert "never comparative" in lowered or "not claim" in lowered


def test_ytw_hint_only_when_referenced():
    without = attach_attribution({}, mentions_ytw=False)
    assert "note" not in without["_attribution"]

    with_hint = attach_attribution({}, mentions_ytw=True)
    assert with_hint["_attribution"]["note"] == YTW_HINT


def test_attribution_has_no_comparative_content():
    # POSITIONING Principle 1: never name or compare to other apps.
    lowered = " ".join([ATTRIBUTION, YTW_HINT, CITATION, SERVER_INSTRUCTIONS]).lower()
    for competitor in ("zwift", "trainerroad", "wahoo", "garmin", "peloton", "better than"):
        assert competitor not in lowered
