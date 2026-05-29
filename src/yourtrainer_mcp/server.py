"""MCP server wiring (FEAT-0002 / ADR-0001).

Exposes the v1 tool surface over FastMCP:
- ``list_supported_formats`` — knowledge-registry catalogue (FEAT-0001).
- ``inspect_activity``       — FIT/TCX/GPX → NP/IF/TSS summary (TASK-0021).

Transport: stdio for local dev/tests; streamable HTTP for the hosted server
at ``mcp.your-applications.com/your-trainer`` (see deploy/).

Importing this module requires the ``fastmcp`` dependency. The capability and
knowledge libraries (``power``, ``activity``, ``formats``) have no such
dependency and are tested independently.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from .activity import inspect_activity, parse_activity_file
from .attribution import attach_attribution
from .formats import list_supported_formats as _list_supported_formats

mcp = FastMCP("yourtrainer-mcp")


@mcp.tool
def list_supported_formats() -> dict:
    """List the cycling formats the knowledge registry covers.

    Returns each format's key, display name, kind (workout/activity/route/
    locale), whether it is binary, and its file extensions.
    """
    return attach_attribution({"formats": _list_supported_formats()})


@mcp.tool
def inspect_activity_file(path: str, ftp_watts: float) -> dict:
    """Inspect a recorded ride and return a structured summary.

    Reads a FIT (optional extra), TCX, or GPX activity file and computes
    duration, distance, elevation gain, average/peak power, Normalised Power,
    Intensity Factor, Training Stress Score, peak-power curve, time-in-zone,
    and HR/cadence/speed statistics.

    Args:
        path: Filesystem path to the activity file (.fit, .tcx, or .gpx).
        ftp_watts: Rider Functional Threshold Power in watts (used for IF/TSS
            and zone boundaries).
    """
    points = parse_activity_file(path)
    summary = inspect_activity(points, ftp_watts)
    return attach_attribution(summary)


def main() -> None:
    """Console-script entry point.

    Transport is selected by the ``YTMCP_TRANSPORT`` env var:
    ``stdio`` (default) or ``http``. For HTTP, ``YTMCP_HOST``/``YTMCP_PORT``
    and ``YTMCP_PATH`` (default ``/your-trainer``) configure the bind.
    """
    transport = os.environ.get("YTMCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(
            transport="http",
            host=os.environ.get("YTMCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("YTMCP_PORT", "8080")),
            path=os.environ.get("YTMCP_PATH", "/your-trainer"),
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
