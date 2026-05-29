"""Library-migration helper + conversion roundtrip harness (TASK-0031, TASK-0032).

These are LLM-assist tools: the LLM does the actual text-to-text conversion
(per ADR/phase scope), while these tools inventory the work and verify the
result so the agent can self-correct.
"""

from __future__ import annotations

from pathlib import Path

from . import workout as wk
from .detect import detect_format

# Suggested canonical target per source-format kind.
_WORKOUT_FORMATS = {"zwo", "erg", "mrc", "ytw"}


def migration_inventory(paths: list[str], target_format: str = "ytw") -> dict:
    """Inventory a set of files for a batch conversion.

    Detects each file's format and groups them; flags which need conversion to
    ``target_format``. The LLM performs the conversions; this scopes the job.
    """
    items: list[dict] = []
    counts: dict[str, int] = {}
    needs_conversion = 0
    for pth in paths:
        p = Path(pth)
        head = p.read_bytes()[:512] if p.exists() else None
        key = detect_format(p.name, head)
        counts[key or "unknown"] = counts.get(key or "unknown", 0) + 1
        is_workout = key in _WORKOUT_FORMATS
        convert = is_workout and key != target_format
        if convert:
            needs_conversion += 1
        items.append({
            "file": p.name,
            "detected_format": key,
            "is_workout": is_workout,
            "needs_conversion": convert,
        })
    return {
        "files": len(paths),
        "by_format": counts,
        "target_format": target_format,
        "needs_conversion": needs_conversion,
        "items": items,
    }


def _to_workout(doc: str, fmt: str) -> wk.Workout:
    fmt = fmt.lower()
    if fmt == "zwo":
        return wk.from_zwo(doc)
    if fmt == "ytw":
        return wk.from_ytw(doc)
    raise wk.WorkoutError(f"roundtrip supports zwo/ytw, not '{fmt}'")


def roundtrip_workout(
    original: str,
    original_format: str,
    converted: str,
    converted_format: str,
    ftp: float = 250.0,
) -> dict:
    """Compare a converted workout against the original, reporting loss.

    Parses both, expands each to a per-second power series, and measures the
    difference. Lets an agent verify and self-correct a conversion (ZWO/.ytw).
    """
    w_orig = _to_workout(original, original_format)
    w_conv = _to_workout(converted, converted_format)
    s_orig = wk.expand_to_power_series(w_orig, ftp)
    s_conv = wk.expand_to_power_series(w_conv, ftp)

    duration_match = len(s_orig) == len(s_conv)
    n = min(len(s_orig), len(s_conv))
    diffs = [abs(s_orig[i] - s_conv[i]) for i in range(n)]
    max_dev = max(diffs) if diffs else 0.0
    mean_dev = sum(diffs) / n if n else 0.0
    lossless = duration_match and max_dev <= 0.5  # ≤0.5 W on the FTP-scaled series
    return {
        "duration_match": duration_match,
        "original_duration_s": len(s_orig),
        "converted_duration_s": len(s_conv),
        "max_deviation_w": round(max_dev, 2),
        "mean_deviation_w": round(mean_dev, 3),
        "lossless": lossless,
    }
