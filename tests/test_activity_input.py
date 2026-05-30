"""Activity tools accept base64 alongside path (TASK-0065).

Single-activity tools work from a server-readable path (local/stdio) OR inline
base64 content (remote/hosted, e.g. the mobile app). Covers the acceptance
matrix and the shared _activity_points helper + parse_activity_data core.
"""

from __future__ import annotations

import asyncio
import base64

import pytest

from yourtrainer_mcp import fit, server
from yourtrainer_mcp.activity import UnsupportedActivityFormat, parse_activity_data


def _fit_b64(n: int = 120) -> str:
    data = fit.encode_activity_fit([{"power": 250, "heart_rate": 150} for _ in range(n)])
    return base64.b64encode(data).decode("ascii")


def _run(coro):
    return asyncio.run(coro)


# ---- lib-level bytes dispatcher ----

def test_parse_activity_data_fit():
    data = fit.encode_activity_fit([{"power": 200} for _ in range(60)])
    pts = parse_activity_data(data, "fit")
    assert len(pts) == 60 and pts[0].power_w == 200


def test_parse_activity_data_tcx(tcx_builder):
    pts = parse_activity_data(tcx_builder([200.0] * 10).encode("utf-8"), "tcx")
    assert len(pts) == 10


def test_parse_activity_data_unsupported_format():
    with pytest.raises(UnsupportedActivityFormat):
        parse_activity_data(b"<workout_file/>", "zwo")


# ---- _activity_points alternation (the acceptance matrix) ----

def test_path_only(tmp_path):
    f = tmp_path / "r.fit"
    f.write_bytes(fit.encode_activity_fit([{"power": 250} for _ in range(60)]))
    assert len(server._activity_points(str(f), None, None)) == 60


def test_base64_only():
    assert len(server._activity_points(None, _fit_b64(), None)) == 120


def test_both_provided_rejected(tmp_path):
    f = tmp_path / "r.fit"
    f.write_bytes(fit.encode_activity_fit([{"power": 1} for _ in range(3)]))
    with pytest.raises(ValueError, match="exactly one"):
        server._activity_points(str(f), _fit_b64(), None)


def test_neither_provided_rejected():
    with pytest.raises(ValueError, match="exactly one"):
        server._activity_points(None, None, None)


def test_malformed_base64_rejected():
    with pytest.raises(ValueError, match="base64"):
        server._activity_points(None, "!!! not base64 !!!", None)


def test_oversize_inline_rejected(monkeypatch):
    monkeypatch.setattr(server, "MAX_INLINE_BYTES", 100)
    with pytest.raises(ValueError, match="inline limit"):
        server._activity_points(None, _fit_b64(120), None)


def test_format_mismatch_rejected():
    # A ZWO sent as activity content: detected as 'zwo' -> unsupported activity.
    zwo = base64.b64encode(b"<workout_file><workout></workout></workout_file>").decode()
    with pytest.raises(UnsupportedActivityFormat):
        server._activity_points(None, zwo, None)


def test_source_format_override(tcx_builder):
    data = base64.b64encode(tcx_builder([200.0] * 5).encode("utf-8")).decode()
    assert len(server._activity_points(None, data, "tcx")) == 5


# ---- tool level over the MCP protocol ----

def test_inspect_activity_file_via_base64_over_protocol():
    async def go():
        from fastmcp import Client
        async with Client(server.mcp) as c:
            r = await c.call_tool("inspect_activity_file",
                                  {"ftp_watts": 250, "document_base64": _fit_b64(3600)})
            return r.data

    data = _run(go())
    assert data["power"]["training_stress_score"] == pytest.approx(100.0, abs=1.0)


def test_inspect_activity_file_both_args_errors_over_protocol():
    async def go():
        from fastmcp import Client
        async with Client(server.mcp) as c:
            args = {"ftp_watts": 250, "path": "/x", "document_base64": _fit_b64(3)}
            return await c.call_tool("inspect_activity_file", args)

    with pytest.raises(Exception):  # noqa: B017 - FastMCP raises a ToolError
        _run(go())


def test_detect_file_via_base64():
    async def go():
        from fastmcp import Client
        async with Client(server.mcp) as c:
            r = await c.call_tool("detect_file", {"document_base64": _fit_b64(3)})
            return r.data

    assert _run(go())["detected_format"] == "fit"
