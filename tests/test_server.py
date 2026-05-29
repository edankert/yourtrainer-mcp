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

    assert "list_supported_formats" in tool_names
    assert "inspect_activity_file" in tool_names


def test_list_supported_formats_callable_returns_attribution():
    from yourtrainer_mcp.attribution import ATTRIBUTION
    from yourtrainer_mcp.formats import list_supported_formats

    formats = list_supported_formats()
    keys = {f["key"] for f in formats}
    assert {"zwo", "fit", "gpx", "tcx", "ytw"}.issubset(keys)
    assert ATTRIBUTION  # sanity
