"""Tests for aggregate health metrics (TASK-0017)."""

from __future__ import annotations

from yourtrainer_mcp import health


def setup_function():
    health.reset()


def test_records_aggregate_counts_only():
    health.record("inspect_activity_file", True)
    health.record("inspect_activity_file", True)
    health.record("validate", False)
    snap = health.snapshot()
    assert snap["requests_total"] == 3
    assert snap["errors_total"] == 1
    assert snap["by_tool"]["inspect_activity_file"] == 2
    assert snap["errors_by_tool"]["validate"] == 1
    assert snap["error_rate"] == round(1 / 3, 4)


def test_uptime_reported_when_start_set():
    health.set_start(100.0)
    assert health.snapshot(160.0)["uptime_s"] == 60.0


def test_snapshot_has_no_per_call_detail():
    health.record("x", True)
    snap = health.snapshot()
    # Only aggregate keys; nothing resembling arguments/payloads/ids.
    assert set(snap) == {
        "requests_total", "errors_total", "error_rate",
        "by_tool", "errors_by_tool", "uptime_s", "note",
    }
