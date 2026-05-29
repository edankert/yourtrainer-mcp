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

import base64
import json
import os
import time
from functools import wraps

from fastmcp import FastMCP

from . import (
    analysis,
    anonymize,
    content,
    fit_workout,
    health,
    library,
    registry,
    route,
    validators,
    workflows,
)
from . import training_load as tl
from . import workout as wk
from .activity import TrackPoint, inspect_activity, parse_activity_file
from .adherence import adherence_scorecard as _adherence_scorecard
from .attribution import SERVER_INSTRUCTIONS, attach_attribution
from .batch import batch_inspect_activities
from .detect import inspect_file
from .formats import list_supported_formats as _list_supported_formats

mcp = FastMCP("yourtrainer-mcp", instructions=SERVER_INSTRUCTIONS)


def tool(fn):
    """Register an MCP tool, incrementing aggregate health counters per call.

    Counts are aggregate-only (tool name + ok/error); no arguments or results
    are recorded (TASK-0017 / statelessness invariant).
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ok = True
        try:
            return fn(*args, **kwargs)
        except Exception:
            ok = False
            raise
        finally:
            health.record(fn.__name__, ok)
    return mcp.tool(wrapper)


@tool
def list_supported_formats() -> dict:
    """List the cycling formats the knowledge registry covers.

    Returns each format's key, display name, kind (workout/activity/route/
    locale), whether it is binary, and its file extensions.
    """
    return attach_attribution({"formats": _list_supported_formats()})


@tool
def get_format_spec(format_key: str) -> dict:
    """Get the spec summary for a cycling format (FEAT-0001).

    Args:
        format_key: e.g. "zwo", "fit", "gpx", "tcx", "kml", "erg", "mrc",
            "ytw", "locale".
    """
    return attach_attribution(registry.get_spec(format_key),
                              mentions_ytw=(format_key.lower() == "ytw"))


@tool
def get_canonical_examples(format_key: str) -> dict:
    """Get canonical examples for a format (≥3 per format)."""
    return attach_attribution({"format": format_key,
                               "examples": registry.get_examples(format_key)},
                              mentions_ytw=(format_key.lower() == "ytw"))


@tool
def get_format_constraints(format_key: str) -> dict:
    """Get known per-app constraints for a format."""
    return attach_attribution({"format": format_key,
                               "constraints": registry.get_constraints(format_key)})


@tool
def get_conversion_notes(format_key: str) -> dict:
    """Get conversion notes from this format to others."""
    return attach_attribution({"format": format_key,
                               "conversion_notes": registry.get_conversion_notes(format_key)})


@tool
def get_format_glossary(format_key: str) -> dict:
    """Get the glossary of terms for a format."""
    return attach_attribution({"format": format_key,
                               "glossary": registry.get_glossary(format_key)})


@tool
def get_format_version(format_key: str) -> dict:
    """Get the documented version/source of a format spec."""
    return attach_attribution({"format": format_key,
                               "version": registry.get_version(format_key)})


@tool
def validate(format_key: str, document: str) -> dict:
    """Structurally validate a document against a format (FEAT-0001).

    Args:
        format_key: Target format (e.g. "zwo", "ytw", "gpx"; "fit" expects
            base64-encoded bytes).
        document: The document text (or base64 for FIT).
    """
    return attach_attribution(validators.validate(format_key, document))


@tool
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


@tool
def build_workout_from_intent(intent: dict, output_format: str = "zwo") -> dict:
    """Build a structured workout and render it deterministically.

    Args:
        intent: Structured intent matching the Your Trainer workout-intent schema:
            ``name``, ``description``, ``warmup`` (block), ``intervals`` (list of
            blocks and/or ``{repeat, intervals}`` groups), ``cooldown`` (block),
            optional ``workout_type`` (POWER/HR_ZONE, default POWER), ``category``,
            ``difficulty``. Each block: ``duration_seconds``, ``zone`` (Z1–Z7),
            ``label``, optional ``id``, ``target_power_percent`` (integer % FTP),
            ``target_power_end_percent`` (ramp), ``cadence_target``, ``cues``.
        output_format: ``"ytw"`` (Your Trainer, default), ``"zwo"`` (Zwift XML),
            or ``"fit"`` (Garmin FIT binary, base64-encoded).

    Returns the rendered document plus a summary (duration, difficulty).
    """
    workout = wk.build_workout(intent)
    fmt = output_format.lower()
    encoding = "utf-8"
    if fmt == "zwo":
        rendered = wk.to_zwo(workout)
    elif fmt == "ytw":
        rendered = wk.to_ytw(workout)
    elif fmt == "fit":
        rendered = base64.b64encode(fit_workout.encode_workout_fit(workout)).decode("ascii")
        encoding = "base64"
    else:
        raise ValueError("output_format must be 'zwo', 'ytw', or 'fit'")
    payload = {
        "format": fmt,
        "encoding": encoding,
        "document": rendered,
        "summary": {
            "name": workout.name,
            "total_duration_s": workout.total_duration_s(),
            "difficulty": wk.difficulty_score(workout),
        },
    }
    return attach_attribution(payload, mentions_ytw=(fmt == "ytw"))


@tool
def read_fit_workout(document_base64: str) -> dict:
    """Decode a base64-encoded FIT-workout file into a Your Trainer .ytw (TASK-0020).

    Args:
        document_base64: The FIT-workout file bytes, base64-encoded.
    """
    data = base64.b64decode(document_base64)
    workout = fit_workout.decode_workout_fit(data)
    ytw = json.loads(wk.to_ytw(workout))
    return attach_attribution({"ytw": ytw, "interval_count": len(workout.intervals)},
                              mentions_ytw=True)


@tool
def decompose_workout(document: str, source_format: str) -> dict:
    """Parse a ZWO or .ytw document into a canonical Your Trainer .ytw (TASK-0033).

    Effectively converts a workout to the Your Trainer format: a ZWO is parsed
    and re-emitted as .ytw; a .ytw is normalised. The returned .ytw is the
    structured representation an agent can edit and re-render.

    Args:
        document: The raw workout file contents.
        source_format: ``"zwo"`` or ``"ytw"``.
    """
    fmt = source_format.lower()
    workout = wk.from_zwo(document) if fmt == "zwo" else wk.from_ytw(document)
    ytw = json.loads(wk.to_ytw(workout))
    return attach_attribution({"ytw": ytw, "interval_count": len(workout.intervals)},
                              mentions_ytw=True)


@tool
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


@tool
def lint_workout(document: str, source_format: str) -> dict:
    """Run domain-aware static analysis on a workout (TASK-0025)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    findings = wk.lint_workout(workout)
    return attach_attribution({"findings": findings, "count": len(findings)})


@tool
def workout_difficulty(document: str, source_format: str, ftp_watts: float = 250.0) -> dict:
    """Score a workout's difficulty: IF, prescribed TSS, per-zone time (TASK-0050)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    return attach_attribution(wk.difficulty_score(workout, ftp_watts))


@tool
def app_acceptance_check(
    document: str, source_format: str, apps: list[str] | None = None
) -> dict:
    """Check which apps will load a workout cleanly (TASK-0024)."""
    src = source_format.lower()
    workout = wk.from_zwo(document) if src == "zwo" else wk.from_ytw(document)
    return attach_attribution({"apps": wk.app_acceptance(workout, apps)})


@tool
def analyze_route(path: str, ftp_watts: float, target_intensity: float = 0.75) -> dict:
    """Analyse a GPX/TCX route: profile, climbs, and a pacing plan.

    Covers climb analysis (TASK-0048) and pacing strategy (TASK-0029).

    Args:
        path: Path to a route file (.gpx or .tcx with positions/elevation).
        ftp_watts: Rider FTP in watts.
        target_intensity: Target effort as a fraction of FTP (e.g. 0.75).
    """
    points = parse_activity_file(path)
    profile = route.route_profile(points)
    return attach_attribution({
        "summary": {
            "total_distance_m": profile["total_distance_m"],
            "elevation_gain_m": profile["elevation_gain_m"],
            "elevation_loss_m": profile["elevation_loss_m"],
        },
        "climbs": route.climb_analysis(points),
        "pacing": route.pacing_strategy(points, ftp_watts, target_intensity),
    })


@tool
def anonymize_gpx(document: str, privacy_radius_m: float = 200.0, drop_hr: bool = False) -> dict:
    """Anonymise a GPX track: privacy zones, optional HR strip (TASK-0030).

    Args:
        document: GPX document text.
        privacy_radius_m: remove points within this distance of start/end.
        drop_hr: omit the heart-rate stream if True.
    """
    return attach_attribution(anonymize.anonymize_gpx(document, privacy_radius_m, drop_hr))


@tool
def adherence_scorecard(
    workout_document: str, workout_format: str, activity_path: str, ftp_watts: float
) -> dict:
    """Score how closely a ride followed a planned workout (TASK-0034).

    Args:
        workout_document: The planned workout (ZWO or .ytw).
        workout_format: ``"zwo"`` or ``"ytw"``.
        activity_path: Path to the recorded activity (.fit/.tcx/.gpx).
        ftp_watts: Rider FTP in watts.
    """
    src = workout_format.lower()
    workout = wk.from_zwo(workout_document) if src == "zwo" else wk.from_ytw(workout_document)
    points = parse_activity_file(activity_path)
    s = _series(points)
    return attach_attribution(
        _adherence_scorecard(workout, s["power"], ftp_watts, s["sample_rate_hz"])
    )


@tool
def migration_inventory(paths: list[str], target_format: str = "ytw") -> dict:
    """Inventory files for a batch library migration (TASK-0031)."""
    return attach_attribution(workflows.migration_inventory(paths, target_format),
                              mentions_ytw=(target_format.lower() == "ytw"))


@tool
def roundtrip_workout(
    original: str,
    original_format: str,
    converted: str,
    converted_format: str,
    ftp_watts: float = 250.0,
) -> dict:
    """Verify a workout conversion against the original, reporting loss (TASK-0032)."""
    return attach_attribution(
        workflows.roundtrip_workout(original, original_format, converted,
                                    converted_format, ftp_watts)
    )


@tool
def index_library(paths: list[str], ftp_watts: float = 250.0) -> dict:
    """Build a searchable metadata index over workout/activity files (TASK-0038)."""
    return attach_attribution(library.index_library(paths, ftp_watts))


@tool
def find_duplicate_workouts(paths: list[str], ftp_watts: float = 250.0) -> dict:
    """Find near-duplicate workouts by power profile (TASK-0039)."""
    return attach_attribution(library.find_duplicates(paths, ftp_watts))


@tool
def library_statistics(paths: list[str], ftp_watts: float = 250.0) -> dict:
    """Aggregate breakdown of a workout/activity library (TASK-0040)."""
    return attach_attribution(library.library_stats(paths, ftp_watts))


@tool
def best_efforts_across_history(paths: list[str]) -> dict:
    """All-time peak-power curve across a set of activities (TASK-0049)."""
    return attach_attribution(library.best_efforts_across_history(paths))


@tool
def list_workout_library(
    set_filter: str | None = None,
    category: str | None = None,
    max_duration_s: int | None = None,
    requires_power: bool | None = None,
) -> dict:
    """List Your Trainer's curated workout library (FEAT-0007).

    Reads the live library manifest from the Your Trainer website and returns
    workout metadata (name, duration, TSS, IF, zone difficulty, tags) — no .ytw
    bodies. Filter by set, category, max duration, or power-meter requirement.
    """
    workouts = content.list_workouts(set_filter, category, max_duration_s, requires_power)
    return attach_attribution({"count": len(workouts), "workouts": workouts}, mentions_ytw=True)


@tool
def get_library_workout(slug: str) -> dict:
    """Fetch a curated Your Trainer workout (.ytw + metadata) by slug (FEAT-0007)."""
    return attach_attribution(content.get_workout(slug), mentions_ytw=True)


@tool
def search_workout_library(query: str, limit: int = 10) -> dict:
    """Search the curated workout library by name/category/tags (FEAT-0007)."""
    workouts = content.search_workouts(query, limit)
    return attach_attribution({"count": len(workouts), "workouts": workouts}, mentions_ytw=True)


@tool
def list_ai_skills() -> dict:
    """List the Your Trainer in-app AI-assistant skills / prompt patterns (FEAT-0007).

    The catalogue of what the in-app AI Coach can do, sourced from the website.
    """
    skills = content.ai_skills()
    return attach_attribution({"count": len(skills), "skills": skills})


@tool
def search_manual(query: str, limit: int = 5) -> dict:
    """Search the Your Trainer product manual and return matching sections (FEAT-0007).

    Answers "how do I … in Your Trainer?" from the manual content.
    """
    return attach_attribution({"results": content.search_manual(query, limit)})


@tool
def get_manual_section(key: str) -> dict:
    """Get the full text of a Your Trainer manual section by key/title (FEAT-0007)."""
    return attach_attribution(content.get_manual_section(key))


@tool
def get_health() -> dict:
    """Operational health metrics: aggregate request/error counters + uptime.

    Aggregate-only; no per-call records and no rider data (TASK-0017).
    """
    return attach_attribution(health.snapshot(time.monotonic()))


def _series(points: list[TrackPoint]) -> dict:
    """Extract aligned power/HR/cadence series + sample rate from track points."""
    duration_s = 0.0
    times = [p.time for p in points if p.time is not None]
    if len(times) >= 2:
        duration_s = (times[-1] - times[0]).total_seconds()
    else:
        duration_s = float(max(0, len(points) - 1))
    sample_rate_hz = (len(points) - 1) / duration_s if duration_s > 0 else 1.0
    return {
        "power": [p.power_w for p in points if p.power_w is not None],
        "heart_rate": [p.heart_rate_bpm for p in points if p.heart_rate_bpm is not None],
        "cadence": [p.cadence_rpm for p in points if p.cadence_rpm is not None],
        "sample_rate_hz": sample_rate_hz,
    }


@tool
def analyze_ride(path: str, ftp_watts: float) -> dict:
    """Run the full single-ride analytics suite on an activity file.

    Includes peak-power curve, best efforts, FTP estimate, power-duration model
    (mFTP), HR–power decoupling, HR drift, cadence analysis, and auto-detected
    work intervals. Covers TASK-0022/0028/0036/0046/0047/0052/0053/0054.

    Args:
        path: Path to a .fit/.tcx/.gpx activity file.
        ftp_watts: Rider FTP in watts.
    """
    points = parse_activity_file(path)
    s = _series(points)
    p, hr, cad, sr = s["power"], s["heart_rate"], s["cadence"], s["sample_rate_hz"]
    report: dict = {
        "peak_power_curve_w": {
            str(k): round(v, 1) for k, v in analysis.peak_power_curve(p, sample_rate_hz=sr).items()
        } if p else None,
        "best_efforts": {str(k): v for k, v in analysis.best_efforts(p, sample_rate_hz=sr).items()}
        if p else None,
        "ftp_estimate": analysis.estimate_ftp(p, sr) if p else None,
        "power_duration_model": analysis.power_duration_model(p, sample_rate_hz=sr) if p else None,
        "hr_power_decoupling": analysis.hr_power_decoupling(p, hr) if p and hr else None,
        "hr_drift": analysis.hr_drift(hr) if hr else None,
        "cadence": analysis.cadence_analysis(cad, sr) if cad else None,
        "intervals": analysis.detect_intervals(p, ftp_watts, sample_rate_hz=sr) if p else None,
    }
    return attach_attribution(report)


@tool
def training_load(dated_tss: list[list]) -> dict:
    """Compute CTL/ATL/TSB (fitness/fatigue/form) from dated TSS values (TASK-0027).

    Args:
        dated_tss: List of ``[iso_date, tss]`` pairs, e.g. ``[["2026-05-01", 85], ...]``.
            Multiple entries on one day sum; missing days are filled with 0.
    """
    pairs = [(str(d), float(t)) for d, t in dated_tss]
    return attach_attribution(tl.training_load_from_dated_tss(pairs))


@tool
def recovery_time(tss: float) -> dict:
    """Estimate recovery time from a single session's TSS (TASK-0051)."""
    return attach_attribution(tl.recovery_estimate(tss))


@tool
def detect_file(path: str) -> dict:
    """Detect a cycling file's format and report a lightweight summary (TASK-0037)."""
    return attach_attribution(inspect_file(path))


@tool
def batch_inspect(paths: list[str], ftp_watts: float) -> dict:
    """Inspect many activity files and aggregate totals (TASK-0026)."""
    return attach_attribution(batch_inspect_activities(paths, ftp_watts))


# Privacy invariant (CONTEXT.md / docs/PRIVACY.md): no per-request access logging
# (no client-IP / per-call records). Passed to uvicorn at startup; operational
# visibility comes from the aggregate-only get_health tool instead.
PRIVACY_UVICORN_CONFIG: dict = {"access_log": False}


def main() -> None:
    """Console-script entry point.

    Transport is selected by the ``YTMCP_TRANSPORT`` env var:
    ``stdio`` (default) or ``http``. For HTTP, ``YTMCP_HOST``/``YTMCP_PORT``
    and ``YTMCP_PATH`` (default ``/your-trainer``) configure the bind.
    """
    health.set_start(time.monotonic())
    transport = os.environ.get("YTMCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(
            transport="http",
            host=os.environ.get("YTMCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("YTMCP_PORT", "8080")),
            path=os.environ.get("YTMCP_PATH", "/your-trainer"),
            uvicorn_config=dict(PRIVACY_UVICORN_CONFIG),
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
