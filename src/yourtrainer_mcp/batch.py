"""Batch operations adapter (TASK-0026).

Runs an activity inspection across many files and aggregates the results.
Per-file failures are captured, not fatal — the batch still returns totals for
the files that parsed. Stateless: nothing is written or retained.
"""

from __future__ import annotations

from pathlib import Path

from .activity import inspect_activity, parse_activity_file

ACTIVITY_EXTS = {".fit", ".tcx", ".gpx"}


def batch_inspect_activities(paths: list[str], ftp_watts: float) -> dict:
    """Inspect each activity file; aggregate duration / distance / TSS.

    Returns per-file results (summary or error) plus totals across the files
    that parsed successfully.
    """
    results: list[dict] = []
    total_duration = 0.0
    total_distance = 0.0
    total_tss = 0.0
    ok = 0
    for p in paths:
        name = Path(p).name
        try:
            points = parse_activity_file(p)
            summary = inspect_activity(points, ftp_watts)
            results.append({"file": name, "ok": True, "summary": summary})
            ok += 1
            total_duration += summary["duration_s"]
            total_distance += summary["distance_m"]
            if summary.get("power"):
                total_tss += summary["power"]["training_stress_score"]
        except Exception as exc:  # noqa: BLE001 - batch must not abort on one bad file
            results.append({"file": name, "ok": False, "error": str(exc)})
    return {
        "files": len(paths),
        "parsed": ok,
        "failed": len(paths) - ok,
        "totals": {
            "duration_s": round(total_duration, 1),
            "distance_m": round(total_distance, 1),
            "training_stress_score": round(total_tss, 1),
        },
        "results": results,
    }
