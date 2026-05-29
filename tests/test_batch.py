"""Tests for the batch operations adapter (TASK-0026)."""

from __future__ import annotations

from yourtrainer_mcp import fit
from yourtrainer_mcp.batch import batch_inspect_activities


def test_batch_aggregates_and_survives_bad_files(tmp_path):
    good = tmp_path / "good.fit"
    good.write_bytes(fit.encode_activity_fit([{"power": 250} for _ in range(600)]))
    bad = tmp_path / "bad.fit"
    bad.write_bytes(b"not a fit file")

    out = batch_inspect_activities([str(good), str(bad)], ftp_watts=250.0)
    assert out["files"] == 2
    assert out["parsed"] == 1
    assert out["failed"] == 1
    assert out["totals"]["training_stress_score"] > 0
    # One result ok, one error captured.
    assert {r["ok"] for r in out["results"]} == {True, False}
