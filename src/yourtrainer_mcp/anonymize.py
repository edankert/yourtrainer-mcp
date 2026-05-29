"""Activity privacy / anonymisation (TASK-0030).

Removes personally identifying detail from a GPX track: drops points inside a
privacy radius around the start and end (home/work geofencing), optionally
strips the heart-rate stream, and re-emits a clean canonical GPX that carries
no device/creator metadata. Stateless — input in, anonymised output out.

GPX is the supported interchange here; TCX/FIT users convert to GPX first.
"""

from __future__ import annotations

from typing import cast

from .activity import _haversine_m, parse_gpx


def _emit_gpx(points: list, drop_hr: bool) -> str:
    rows = []
    for p in points:
        parts = [f'    <trkpt lat="{p.lat:.6f}" lon="{p.lon:.6f}">']
        if p.altitude_m is not None:
            parts.append(f"      <ele>{p.altitude_m:g}</ele>")
        if p.time is not None:
            parts.append(f"      <time>{p.time.isoformat().replace('+00:00', 'Z')}</time>")
        ext = []
        if p.power_w is not None:
            ext.append(f"<power>{int(p.power_w)}</power>")
        if p.cadence_rpm is not None:
            ext.append(f"<cad>{int(p.cadence_rpm)}</cad>")
        if p.heart_rate_bpm is not None and not drop_hr:
            ext.append(f"<hr>{int(p.heart_rate_bpm)}</hr>")
        if ext:
            parts.append("      <extensions>" + "".join(ext) + "</extensions>")
        parts.append("    </trkpt>")
        rows.append("\n".join(parts))
    body = "\n".join(rows)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gpx version="1.1" creator="yourtrainer-mcp" '
        'xmlns="http://www.topografix.com/GPX/1/1">\n'
        "  <trk><trkseg>\n"
        f"{body}\n"
        "  </trkseg></trk>\n"
        "</gpx>\n"
    )


def anonymize_gpx(
    text: str,
    privacy_radius_m: float = 200.0,
    drop_hr: bool = False,
) -> dict:
    """Anonymise a GPX track.

    Args:
        text: GPX document.
        privacy_radius_m: points within this distance of the original start or
            end coordinate are removed.
        drop_hr: if True, omit the heart-rate stream.

    Returns the anonymised GPX plus a summary of what was removed.
    """
    points = [p for p in parse_gpx(text) if p.lat is not None and p.lon is not None]
    if not points:
        return {"gpx": _emit_gpx([], drop_hr), "removed_points": 0, "kept_points": 0}

    # lat/lon are guaranteed non-None by the filter above.
    slat, slon = cast(float, points[0].lat), cast(float, points[0].lon)
    elat, elon = cast(float, points[-1].lat), cast(float, points[-1].lon)
    kept = []
    removed = 0
    for p in points:
        plat, plon = cast(float, p.lat), cast(float, p.lon)
        near_start = _haversine_m(slat, slon, plat, plon) <= privacy_radius_m
        near_end = _haversine_m(elat, elon, plat, plon) <= privacy_radius_m
        if near_start or near_end:
            removed += 1
            continue
        kept.append(p)
    return {
        "gpx": _emit_gpx(kept, drop_hr),
        "removed_points": removed,
        "kept_points": len(kept),
        "privacy_radius_m": privacy_radius_m,
        "hr_dropped": drop_hr,
        "note": "Start/end privacy zones removed; device/creator metadata not re-emitted.",
    }
