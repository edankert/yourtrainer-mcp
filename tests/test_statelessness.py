"""Statelessness / privacy invariant suite (TASK-0064).

Enforces the CONTEXT.md guarantee: the server retains NO rider/user content.
User input (activity files, uploaded documents) is read, processed in memory,
and discarded — never written to disk and never held across calls. The only
cross-call state is aggregate health counters and a cache of *public* Your
Trainer website content. These tests fail if a future change breaks that.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest

from yourtrainer_mcp import content, fit, health
from yourtrainer_mcp import workout as wk
from yourtrainer_mcp.activity import inspect_activity, parse_activity_file
from yourtrainer_mcp.anonymize import anonymize_gpx

WEB = Path(__file__).parent / "fixtures" / "website"

_INTENT = {
    "name": "Priv", "description": "d", "workout_type": "POWER",
    "warmup": {"duration_seconds": 300, "zone": "Z2", "label": "Warmup",
               "target_power_percent": 40, "target_power_end_percent": 70},
    "intervals": [{"duration_seconds": 600, "zone": "Z3", "label": "Work",
                   "target_power_percent": 88}],
    "cooldown": {"duration_seconds": 300, "zone": "Z1", "label": "Cooldown",
                 "target_power_percent": 50},
}


@pytest.fixture(autouse=True)
def _reset_state():
    health.reset()
    content.clear_cache()
    yield
    health.reset()
    content.clear_cache()
    content._fetcher = content._urllib_fetch  # restore default fetcher
    content._base_url = content.DEFAULT_BASE_URL


def _local_fetch(url: str) -> str:
    path = url.split("/your-trainer/", 1)[1]
    return (WEB / path).read_text(encoding="utf-8")


def test_processing_user_content_never_enters_the_content_cache(tmp_path):
    # A rider's activity file + an authored workout + an uploaded GPX.
    ride = tmp_path / "ride.fit"
    ride.write_bytes(fit.encode_activity_fit([{"power": 250, "heart_rate": 150}
                                              for _ in range(120)]))
    inspect_activity(parse_activity_file(ride), 250.0)
    w = wk.build_workout(_INTENT)
    wk.to_ytw(w)
    wk.to_zwo(w)
    anonymize_gpx("<gpx><trk><trkseg><trkpt lat='52.1' lon='5.2'/></trkseg></trk></gpx>")
    # None of that touches the public-content cache.
    assert content._cache == {}


def test_content_cache_holds_only_public_site_paths():
    content.set_fetcher(_local_fetch)
    content.list_workouts()
    content.get_workout("sweet-spot-3x10min-at-88pct-ftp")
    content.manual_sections()
    content.ai_skills()
    assert content._cache  # populated with public content
    for key in content._cache:
        assert key in {"library/manifest.json", "manual.html", "ai-skills.html"} \
            or key.endswith(".ytw"), key  # only site content paths


def test_health_metrics_are_aggregate_only():
    health.record("inspect_activity_file", True)
    health.record("inspect_activity_file", True)
    health.record("validate", False)
    snap = health.snapshot()
    # Exactly the aggregate keys — nothing resembling args, payloads, or ids.
    assert set(snap) == {"requests_total", "errors_total", "error_rate",
                         "by_tool", "errors_by_tool", "uptime_s", "note"}
    # Keys are tool names; values are integer counts (no user content).
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in snap["by_tool"].items())


def test_no_working_files_written_during_processing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ride = tmp_path / "in.fit"
    ride.write_bytes(fit.encode_activity_fit([{"power": 200} for _ in range(60)]))
    before = set(os.listdir(tmp_path))
    inspect_activity(parse_activity_file(ride), 250.0)
    wk.to_ytw(wk.build_workout(_INTENT))
    # Processing created no files (only the input we wrote remains).
    assert set(os.listdir(tmp_path)) == before == {"in.fit"}


def test_repeated_calls_are_independent_no_cross_call_bleed():
    a = wk.difficulty_score(wk.build_workout(_INTENT))
    other = dict(_INTENT, name="Other",
                 intervals=[{"duration_seconds": 1200, "zone": "Z4", "label": "Hard",
                             "target_power_percent": 105}])
    b = wk.difficulty_score(wk.build_workout(other))
    a_again = wk.difficulty_score(wk.build_workout(_INTENT))
    assert a == a_again and a != b


def test_http_transport_disables_request_access_logging():
    # The HTTP entrypoint passes access_log=False to uvicorn (no per-request /
    # client-IP records). uvicorn reconfigures logging at startup, so this MUST
    # go through its config, not a pre-disabled logger.
    from yourtrainer_mcp import server
    assert server.PRIVACY_UVICORN_CONFIG["access_log"] is False


def test_package_emits_no_log_records():
    # Our code attaches no logging handlers and emits no records (so it cannot
    # leak user content into logs). Capture anything logged under the package.
    records: list[logging.LogRecord] = []

    class _Catch(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger = logging.getLogger("yourtrainer_mcp")
    handler = _Catch()
    logger.addHandler(handler)
    logger.propagate = True
    try:
        ride = fit.encode_activity_fit([{"power": 250} for _ in range(60)])
        import io
        # exercise a few code paths
        wk.to_ytw(wk.build_workout(_INTENT))
        assert ride[:4] != b""  # touch the bytes
        _ = io  # silence
    finally:
        logger.removeHandler(handler)
    assert records == []
