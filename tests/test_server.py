"""Server wiring smoke test (FEAT-0002). Skipped when fastmcp is absent."""

from __future__ import annotations

import pytest

pytest.importorskip("fastmcp")


def test_tools_are_registered():
    import asyncio
    import inspect

    from yourtrainer_mcp import server

    result = server.mcp.list_tools()
    if inspect.isawaitable(result):
        result = asyncio.run(result)
    tool_names = {getattr(t, "name", None) for t in result}

    expected = {
        "list_supported_formats",
        "get_format_spec",
        "get_canonical_examples",
        "get_format_constraints",
        "get_conversion_notes",
        "get_format_glossary",
        "get_format_version",
        "validate",
        "inspect_activity_file",
        "build_workout_from_intent",
        "read_fit_workout",
        "decompose_workout",
        "scale_workout",
        "lint_workout",
        "workout_difficulty",
        "app_acceptance_check",
        "analyze_ride",
        "training_load",
        "recovery_time",
        "detect_file",
        "batch_inspect",
        "analyze_route",
        "anonymize_gpx",
        "adherence_scorecard",
        "migration_inventory",
        "roundtrip_workout",
        "index_library",
        "find_duplicate_workouts",
        "library_statistics",
        "best_efforts_across_history",
        "get_health",
    }
    assert expected.issubset(tool_names)


def test_list_supported_formats_callable_returns_attribution():
    from yourtrainer_mcp.attribution import ATTRIBUTION
    from yourtrainer_mcp.formats import list_supported_formats

    formats = list_supported_formats()
    keys = {f["key"] for f in formats}
    assert {"zwo", "fit", "gpx", "tcx", "ytw"}.issubset(keys)
    assert ATTRIBUTION  # sanity
