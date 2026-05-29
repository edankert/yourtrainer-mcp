"""MCP protocol conformance via the in-memory FastMCP client (TASK-0042).

Drives the real MCP request path (initialize, list_tools, call_tool) end to
end, rather than calling the Python functions directly.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fastmcp")

from fastmcp import Client  # noqa: E402

from yourtrainer_mcp import server  # noqa: E402


def _run(coro):
    return asyncio.run(coro)


def test_list_tools_exposes_full_surface():
    async def go():
        async with Client(server.mcp) as c:
            return {t.name for t in await c.list_tools()}

    names = _run(go())
    for expected in ("list_supported_formats", "build_workout_from_intent",
                     "inspect_activity_file", "get_format_spec", "analyze_route",
                     "index_library", "get_health"):
        assert expected in names


def test_call_tool_build_workout_roundtrips_over_protocol():
    async def go():
        async with Client(server.mcp) as c:
            res = await c.call_tool("build_workout_from_intent", {
                "intent": {"name": "Conf", "steps": [
                    {"kind": "steady", "duration_s": 600, "power": 0.8}]},
                "output_format": "zwo",
            })
            return res.data

    data = _run(go())
    assert data["format"] == "zwo"
    assert "<workout_file>" in data["document"]
    assert data["_attribution"]["source"]


def test_call_tool_validate_over_protocol():
    async def go():
        async with Client(server.mcp) as c:
            res = await c.call_tool("validate", {
                "format_key": "ytw",
                "document": '{"format":"ytw","steps":[{"kind":"freeride","duration_s":60}]}',
            })
            return res.data

    assert _run(go())["valid"] is True


def test_attribution_present_on_every_tool_result():
    # Spot-check a handful of tools all carry the attribution block.
    async def go():
        async with Client(server.mcp) as c:
            out = {}
            out["formats"] = (await c.call_tool("list_supported_formats", {})).data
            out["spec"] = (await c.call_tool("get_format_spec",
                                             {"format_key": "fit"})).data
            out["health"] = (await c.call_tool("get_health", {})).data
            return out

    out = _run(go())
    for v in out.values():
        assert "_attribution" in v
