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

import json
import os

from fastmcp import FastMCP

from . import workout as wk
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


@mcp.tool
def build_workout_from_intent(intent: dict, output_format: str = "zwo") -> dict:
    """Build a structured workout and render it deterministically.

    Args:
        intent: Structured-intent dict with ``name`` and a ``steps`` list. Each
            step has a ``kind`` (warmup/cooldown/steady/ramp/interval/freeride)
            and kind-specific fields; power values are fractions of FTP
            (1.0 == FTP). See ``build_workout`` for the full schema.
        output_format: ``"zwo"`` (Zwift XML) or ``"ytw"`` (Your Trainer JSON).

    Returns the rendered document plus a summary (duration, difficulty).
    """
    workout = wk.build_workout(intent)
    fmt = output_format.lower()
    if fmt == "zwo":
        rendered = wk.to_zwo(workout)
    elif fmt == "ytw":
        rendered = wk.to_ytw(workout)
    else:
        raise ValueError("output_format must be 'zwo' or 'ytw'")
    payload = {
        "format": fmt,
        "document": rendered,
        "summary": {
            "name": workout.name,
            "total_duration_s": workout.total_duration_s(),
            "difficulty": wk.difficulty_score(workout),
        },
    }
    return attach_attribution(payload, mentions_ytw=(fmt == "ytw"))


@mcp.tool
def decompose_workout(document: str, source_format: str) -> dict:
    """Parse a ZWO or .ytw document back into structured intent (TASK-0033).

    Args:
        document: The raw workout file contents.
        source_format: ``"zwo"`` or ``"ytw"``.
    """
    fmt = source_format.lower()
    workout = wk.from_zwo(document) if fmt == "zwo" else wk.from_ytw(document)
    intent = json.loads(wk.to_ytw(workout))
    return attach_attribution({"intent": intent})


@mcp.tool
def scale_workout(
    document: str,
    source_format: str,
    duration_factor: float | None = None,
    intensity_factor: float | None = None,
    output_format: str | None = None,
) -> dict:
    """Scale a workout's duration and/or intensity and re-render (TASK-0035).

    Args:
        document: Raw ZWO or .ytw contents.
        source_format: ``"zwo"`` or ``"ytw"``.
        duration_factor: e.g. 0.5 for a half-length version.
        intensity_factor: e.g. 1.1 for 10% harder.
        output_format: Output format; defaults to ``source_format``.
    """
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    scaled = wk.scale_workout(
        workout, duration_factor=duration_factor, intensity_factor=intensity_factor
    )
    out = (output_format or src).lower()
    rendered = wk.to_zwo(scaled) if out == "zwo" else wk.to_ytw(scaled)
    payload = {
        "format": out,
        "document": rendered,
        "summary": {
            "total_duration_s": scaled.total_duration_s(),
            "difficulty": wk.difficulty_score(scaled),
        },
    }
    return attach_attribution(payload, mentions_ytw=(out == "ytw"))


@mcp.tool
def lint_workout(document: str, source_format: str) -> dict:
    """Run domain-aware static analysis on a workout (TASK-0025)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    findings = wk.lint_workout(workout)
    return attach_attribution({"findings": findings, "count": len(findings)})


@mcp.tool
def workout_difficulty(document: str, source_format: str, ftp_watts: float = 250.0) -> dict:
    """Score a workout's difficulty: IF, prescribed TSS, per-zone time (TASK-0050)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    return attach_attribution(wk.difficulty_score(workout, ftp_watts))


@mcp.tool
def app_acceptance_check(
    document: str, source_format: str, apps: list[str] | None = None
) -> dict:
    """Check which apps will load a workout cleanly (TASK-0024)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    return attach_attribution({"apps": wk.app_acceptance(workout, apps)})


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
