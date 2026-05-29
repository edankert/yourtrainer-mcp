"""Library-aware operations (FEAT-0006).

Operate over a folder (list) of workout/activity files:
- index_library (TASK-0038): searchable metadata index
- find_duplicates (TASK-0039): near-duplicate workouts
- library_stats (TASK-0040): aggregate breakdown
- best_efforts_across_history (TASK-0049): all-time peak-power curve

Stateless: files are read and summarised; nothing is written or retained.
"""

from __future__ import annotations

from pathlib import Path

from . import analysis
from . import workout as wk
from .activity import inspect_activity, parse_activity_file
from .detect import detect_format
from .power import average

WORKOUT_FORMATS = {"zwo", "ytw"}
ACTIVITY_FORMATS = {"fit", "tcx", "gpx"}


def _read_head(p: Path) -> bytes | None:
    return p.read_bytes()[:512] if p.exists() else None


def _workout_entry(path: Path, fmt: str, ftp: float) -> dict:
    text = path.read_text(encoding="utf-8")
    w = wk.from_zwo(text) if fmt == "zwo" else wk.from_ytw(text)
    diff = wk.difficulty_score(w, ftp)
    return {
        "file": path.name, "format": fmt, "kind": "workout",
        "name": w.name, "duration_s": w.total_duration_s(),
        "tss": diff["tss"], "intensity_factor": diff["intensity_factor"],
        "intervals": len(w.intervals),
    }


def _activity_entry(path: Path, fmt: str, ftp: float) -> dict:
    summary = inspect_activity(parse_activity_file(path), ftp)
    power = summary.get("power") or {}
    return {
        "file": path.name, "format": fmt, "kind": "activity",
        "duration_s": summary["duration_s"], "distance_m": summary["distance_m"],
        "tss": power.get("training_stress_score"),
        "normalized_power_w": power.get("normalized_power_w"),
    }


def index_library(paths: list[str], ftp_watts: float = 250.0) -> dict:
    """Build a searchable metadata index over a set of files."""
    entries: list[dict] = []
    errors: list[dict] = []
    for pth in paths:
        p = Path(pth)
        fmt = detect_format(p.name, _read_head(p))
        try:
            if fmt in WORKOUT_FORMATS:
                entries.append(_workout_entry(p, fmt, ftp_watts))
            elif fmt in ACTIVITY_FORMATS:
                entries.append(_activity_entry(p, fmt, ftp_watts))
            else:
                errors.append({"file": p.name, "error": f"unindexable format: {fmt}"})
        except Exception as exc:  # noqa: BLE001
            errors.append({"file": p.name, "error": str(exc)})
    return {"count": len(entries), "entries": entries, "errors": errors}


def find_duplicates(
    workout_paths: list[str],
    ftp_watts: float = 250.0,
    duration_tolerance_s: int = 30,
    mean_deviation_w: float = 10.0,
) -> dict:
    """Find near-duplicate workouts by comparing power profiles.

    Two workouts are near-duplicates when their total durations are within
    ``duration_tolerance_s`` and the mean absolute difference of their
    per-second power series is within ``mean_deviation_w``.
    """
    loaded: list[tuple[str, list[float]]] = []
    for pth in workout_paths:
        p = Path(pth)
        fmt = detect_format(p.name, _read_head(p))
        if fmt not in WORKOUT_FORMATS:
            continue
        text = p.read_text(encoding="utf-8")
        w = wk.from_zwo(text) if fmt == "zwo" else wk.from_ytw(text)
        loaded.append((p.name, wk.expand_to_power_series(w, ftp_watts)))

    groups: list[list[str]] = []
    assigned: set[int] = set()
    for i in range(len(loaded)):
        if i in assigned:
            continue
        group = [loaded[i][0]]
        for j in range(i + 1, len(loaded)):
            if j in assigned:
                continue
            si, sj = loaded[i][1], loaded[j][1]
            if abs(len(si) - len(sj)) > duration_tolerance_s:
                continue
            n = min(len(si), len(sj))
            if n == 0:
                continue
            md = average([abs(si[k] - sj[k]) for k in range(n)])
            if md <= mean_deviation_w:
                group.append(loaded[j][0])
                assigned.add(j)
        if len(group) > 1:
            assigned.add(i)
            groups.append(group)
    return {"duplicate_groups": groups, "group_count": len(groups)}


def library_stats(paths: list[str], ftp_watts: float = 250.0) -> dict:
    """Aggregate breakdown of a library: counts, durations, TSS."""
    idx = index_library(paths, ftp_watts)
    entries = idx["entries"]
    by_format: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    total_duration = 0.0
    total_tss = 0.0
    for e in entries:
        by_format[e["format"]] = by_format.get(e["format"], 0) + 1
        by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1
        total_duration += e.get("duration_s") or 0
        total_tss += e.get("tss") or 0
    return {
        "files_indexed": idx["count"],
        "by_format": by_format,
        "by_kind": by_kind,
        "total_duration_s": round(total_duration, 1),
        "total_tss": round(total_tss, 1),
        "avg_tss": round(total_tss / len(entries), 1) if entries else 0.0,
        "errors": idx["errors"],
    }


def best_efforts_across_history(
    activity_paths: list[str],
    durations_s: tuple[int, ...] = analysis.STANDARD_DURATIONS_S,
) -> dict:
    """All-time peak-power curve across a set of activities.

    For each duration, the best mean-max power found in any activity, plus the
    file it came from.
    """
    best: dict[int, dict] = {}
    for pth in activity_paths:
        p = Path(pth)
        fmt = detect_format(p.name, _read_head(p))
        if fmt not in ACTIVITY_FORMATS:
            continue
        try:
            points = parse_activity_file(p)
        except Exception:  # noqa: BLE001
            continue
        power = [pt.power_w for pt in points if pt.power_w is not None]
        if not power:
            continue
        ppc = analysis.peak_power_curve(power, durations_s)
        for d, w in ppc.items():
            if d not in best or w > best[d]["watts"]:
                best[d] = {"watts": round(w, 1), "file": p.name}
    return {"best_efforts": {str(d): v for d, v in sorted(best.items())}}
