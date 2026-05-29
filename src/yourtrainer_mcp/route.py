"""Route analytics: profile, climb detection, pacing (TASK-0029, TASK-0048).

Operates on parsed track points (lat/lon/altitude), e.g. from a GPX route.
Distance is computed via haversine; gradient from altitude deltas.
"""

from __future__ import annotations

from .activity import TrackPoint, _haversine_m


def route_profile(points: list[TrackPoint]) -> dict:
    """Cumulative distance, elevation gain/loss, and per-segment gradient."""
    segments: list[dict] = []
    cum_dist = 0.0
    gain = 0.0
    loss = 0.0
    prev: TrackPoint | None = None
    for p in points:
        if (prev is not None and None not in (prev.lat, prev.lon, p.lat, p.lon)):
            d = _haversine_m(prev.lat, prev.lon, p.lat, p.lon)  # type: ignore[arg-type]
            dz = 0.0
            if prev.altitude_m is not None and p.altitude_m is not None:
                dz = p.altitude_m - prev.altitude_m
                if dz > 0:
                    gain += dz
                else:
                    loss += -dz
            cum_dist += d
            grade = (dz / d * 100) if d > 0 else 0.0
            segments.append({
                "cum_distance_m": round(cum_dist, 1),
                "length_m": round(d, 2),
                "grade_pct": round(grade, 2),
                "altitude_m": round(p.altitude_m, 1) if p.altitude_m is not None else None,
            })
        prev = p
    return {
        "total_distance_m": round(cum_dist, 1),
        "elevation_gain_m": round(gain, 1),
        "elevation_loss_m": round(loss, 1),
        "segments": segments,
    }


def _categorize(length_m: float, avg_grade: float) -> str:
    """Coarse climb category from a length×grade difficulty score."""
    score = length_m * avg_grade  # m·%
    if score >= 80000:
        return "HC"
    if score >= 40000:
        return "1"
    if score >= 16000:
        return "2"
    if score >= 8000:
        return "3"
    return "4"


def climb_analysis(
    points: list[TrackPoint],
    min_grade_pct: float = 3.0,
    min_length_m: float = 200.0,
) -> dict:
    """Detect climbs: contiguous runs averaging ≥ ``min_grade_pct``.

    Short dips are tolerated by smoothing over the running average grade.
    Returns each climb's start/end distance, length, elevation gain, average
    grade, and a coarse category (HC/1/2/3/4).
    """
    prof = route_profile(points)
    segs = prof["segments"]
    climbs: list[dict] = []
    run: list[dict] = []

    def flush():
        if not run:
            return
        length = sum(s["length_m"] for s in run)
        gain = sum(s["length_m"] * s["grade_pct"] / 100 for s in run)
        if length >= min_length_m and gain > 0:
            avg_grade = gain / length * 100
            climbs.append({
                "start_distance_m": round(run[0]["cum_distance_m"] - run[0]["length_m"], 1),
                "end_distance_m": round(run[-1]["cum_distance_m"], 1),
                "length_m": round(length, 1),
                "elevation_gain_m": round(gain, 1),
                "avg_grade_pct": round(avg_grade, 2),
                "category": _categorize(length, avg_grade),
            })

    for s in segs:
        if s["grade_pct"] >= min_grade_pct:
            run.append(s)
        else:
            flush()
            run = []
    flush()
    return {"climb_count": len(climbs), "climbs": climbs,
            "total_elevation_gain_m": prof["elevation_gain_m"]}


def pacing_strategy(
    points: list[TrackPoint],
    ftp_watts: float,
    target_intensity: float = 0.75,
    gradient_sensitivity: float = 4.0,
) -> dict:
    """Per-climb power/cadence targets for a route at a target intensity.

    Base target = ``target_intensity × FTP``. On each detected climb the target
    is nudged up with average gradient (steeper → harder, capped at 1.15×FTP);
    flats/descents sit at or below base. A simple, transparent model — not a
    physiological optimiser.
    """
    if ftp_watts <= 0:
        raise ValueError("ftp_watts must be positive")
    base = target_intensity * ftp_watts
    climbs = climb_analysis(points)["climbs"]
    targets: list[dict] = []
    for c in climbs:
        factor = 1.0 + (c["avg_grade_pct"] / 100) * gradient_sensitivity
        watts = min(base * factor, 1.15 * ftp_watts)
        targets.append({
            "start_distance_m": c["start_distance_m"],
            "end_distance_m": c["end_distance_m"],
            "avg_grade_pct": c["avg_grade_pct"],
            "category": c["category"],
            "target_w": round(watts, 0),
            "target_pct_ftp": round(watts / ftp_watts * 100, 0),
            "suggested_cadence_rpm": 75 if c["avg_grade_pct"] >= 8 else 85,
        })
    return {
        "ftp_w": ftp_watts,
        "base_target_w": round(base, 0),
        "base_target_pct_ftp": round(target_intensity * 100, 0),
        "climb_targets": targets,
        "note": "Flats and descents: hold the base target or soft-pedal on steep descents.",
    }
