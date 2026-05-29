"""Activity-file inspector (TASK-0021).

Parses recorded rides (TCX, GPX with stdlib; FIT via the optional ``fitparse``
extra) into a uniform list of ``TrackPoint`` samples, then emits a structured
JSON summary with NP/IF/TSS, peak power, time-in-zone, HR/cadence/speed stats.

Design notes
------------
- TCX/GPX parsing strips XML namespaces and matches on local tag names so it
  tolerates the namespace soup these formats ship with in the wild.
- Power is read from the Garmin TPX extension (TCX) and the power extensions
  commonly used in GPX (``power`` / ``PowerInWatts``).
- The math lives in ``power.py``; this module only extracts and aggregates.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import power as power_math


@dataclass
class TrackPoint:
    time: datetime | None = None
    lat: float | None = None
    lon: float | None = None
    altitude_m: float | None = None
    distance_m: float | None = None  # cumulative, if recorded
    power_w: float | None = None
    heart_rate_bpm: float | None = None
    cadence_rpm: float | None = None
    speed_mps: float | None = None


class UnsupportedActivityFormat(Exception):
    """Raised when a file's format is not a supported activity format."""


def _local(tag: str) -> str:
    """Strip an XML namespace, returning the local tag name."""
    return tag.rsplit("}", 1)[-1]


def _find_local(elem: ET.Element, name: str) -> ET.Element | None:
    for child in elem.iter():
        if _local(child.tag) == name:
            return child
    return None


def _parse_time(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def parse_tcx(text: str) -> list[TrackPoint]:
    root = ET.fromstring(text)
    points: list[TrackPoint] = []
    for tp in root.iter():
        if _local(tp.tag) != "Trackpoint":
            continue
        pt = TrackPoint()
        for el in tp.iter():
            name = _local(el.tag)
            val = (el.text or "").strip()
            if name == "Time":
                pt.time = _parse_time(val)
            elif name == "LatitudeDegrees" and val:
                pt.lat = float(val)
            elif name == "LongitudeDegrees" and val:
                pt.lon = float(val)
            elif name == "AltitudeMeters" and val:
                pt.altitude_m = float(val)
            elif name == "DistanceMeters" and val:
                pt.distance_m = float(val)
            elif name == "Value" and val and _local(_parent_is(tp, el)) == "HeartRateBpm":
                pt.heart_rate_bpm = float(val)
            elif name == "Cadence" and val:
                pt.cadence_rpm = float(val)
            elif name == "Watts" and val:
                pt.power_w = float(val)
            elif name == "Speed" and val:
                pt.speed_mps = float(val)
        points.append(pt)
    return points


def _parent_is(root: ET.Element, target: ET.Element) -> str:
    """Return the tag of ``target``'s parent within ``root`` (or '')."""
    for parent in root.iter():
        for child in list(parent):
            if child is target:
                return parent.tag
    return ""


def parse_gpx(text: str) -> list[TrackPoint]:
    root = ET.fromstring(text)
    points: list[TrackPoint] = []
    for trkpt in root.iter():
        if _local(trkpt.tag) != "trkpt":
            continue
        pt = TrackPoint()
        lat, lon = trkpt.get("lat"), trkpt.get("lon")
        pt.lat = float(lat) if lat else None
        pt.lon = float(lon) if lon else None
        for el in trkpt.iter():
            name = _local(el.tag)
            val = (el.text or "").strip()
            if name == "ele" and val:
                pt.altitude_m = float(val)
            elif name == "time":
                pt.time = _parse_time(val)
            elif name in ("power", "PowerInWatts") and val:
                pt.power_w = float(val)
            elif name in ("hr", "heartrate") and val:
                pt.heart_rate_bpm = float(val)
            elif name in ("cad", "cadence") and val:
                pt.cadence_rpm = float(val)
        points.append(pt)
    return points


def parse_fit(path: Path) -> list[TrackPoint]:
    try:
        from fitparse import FitFile
    except ImportError:
        # Fall back to the built-in codec for standard files (no extra needed).
        return _parse_fit_builtin(path)

    fitfile = FitFile(str(path))
    points: list[TrackPoint] = []
    for record in fitfile.get_messages("record"):
        vals = {d.name: d.value for d in record}
        ts = vals.get("timestamp")
        pt = TrackPoint(
            # fitparse returns sub-epoch values as raw ints ("system time");
            # only accept genuine datetimes, else fall back to 1 Hz timing.
            time=ts if isinstance(ts, datetime) else None,
            altitude_m=vals.get("altitude") or vals.get("enhanced_altitude"),
            distance_m=vals.get("distance"),
            power_w=vals.get("power"),
            heart_rate_bpm=vals.get("heart_rate"),
            cadence_rpm=vals.get("cadence"),
            speed_mps=vals.get("speed") or vals.get("enhanced_speed"),
        )
        semicircle = 180.0 / 2**31
        if vals.get("position_lat") is not None:
            pt.lat = vals["position_lat"] * semicircle
        if vals.get("position_long") is not None:
            pt.lon = vals["position_long"] * semicircle
        points.append(pt)
    return points


def _parse_fit_builtin(path: Path) -> list[TrackPoint]:
    """Parse a standard FIT activity using the built-in codec (no extra)."""
    from datetime import datetime, timedelta, timezone

    from . import fit

    base = datetime(1989, 12, 31, tzinfo=timezone.utc)
    points: list[TrackPoint] = []
    for s in fit.decode_activity(path.read_bytes()):
        pt = TrackPoint(
            power_w=s.get("power"),
            heart_rate_bpm=s.get("heart_rate"),
            cadence_rpm=s.get("cadence"),
            distance_m=s.get("distance_m"),
            altitude_m=s.get("altitude_m"),
            speed_mps=s.get("speed_mps"),
        )
        if "timestamp_s" in s:
            pt.time = base + timedelta(seconds=s["timestamp_s"])
        points.append(pt)
    return points


def parse_activity_file(path: str | Path) -> list[TrackPoint]:
    """Parse an activity file into TrackPoints, dispatching on extension."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".tcx":
        return parse_tcx(path.read_text(encoding="utf-8"))
    if ext == ".gpx":
        return parse_gpx(path.read_text(encoding="utf-8"))
    if ext == ".fit":
        return parse_fit(path)
    raise UnsupportedActivityFormat(f"Unsupported activity format: {ext or path.name}")


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _elapsed_seconds(points: list[TrackPoint]) -> float:
    times = [p.time for p in points if p.time is not None]
    if len(times) >= 2:
        return (times[-1] - times[0]).total_seconds()
    # Fall back to a 1 Hz assumption when timestamps are absent.
    return float(max(0, len(points) - 1))


def _total_distance_m(points: list[TrackPoint]) -> float:
    distances = [p.distance_m for p in points if p.distance_m is not None]
    if distances:
        return max(distances) - min(distances)
    total = 0.0
    prev: TrackPoint | None = None
    for p in points:
        if (
            prev is not None
            and prev.lat is not None
            and prev.lon is not None
            and p.lat is not None
            and p.lon is not None
        ):
            total += _haversine_m(prev.lat, prev.lon, p.lat, p.lon)
        prev = p
    return total


def _elevation_gain_m(points: list[TrackPoint]) -> float:
    gain = 0.0
    prev: float | None = None
    for p in points:
        if p.altitude_m is not None:
            if prev is not None and p.altitude_m > prev:
                gain += p.altitude_m - prev
            prev = p.altitude_m
    return gain


def _stats(values: list[float]) -> tuple[float | None, float | None]:
    """Return (average, peak) or (None, None) for an empty list."""
    if not values:
        return None, None
    return power_math.average(values), max(values)


def inspect_activity(points: list[TrackPoint], ftp: float) -> dict:
    """Build the structured JSON summary for an activity (TASK-0021 schema)."""
    if ftp <= 0:
        raise ValueError("ftp must be positive")

    duration_s = _elapsed_seconds(points)
    sample_rate_hz = (len(points) - 1) / duration_s if duration_s > 0 else 1.0

    power_series = [p.power_w for p in points if p.power_w is not None]
    hr_series = [p.heart_rate_bpm for p in points if p.heart_rate_bpm is not None]
    cad_series = [p.cadence_rpm for p in points if p.cadence_rpm is not None]

    avg_power, peak_power = _stats(power_series)
    avg_hr, peak_hr = _stats(hr_series)
    avg_cad, peak_cad = _stats(cad_series)

    distance_m = _total_distance_m(points)
    avg_speed_mps = distance_m / duration_s if duration_s > 0 else None

    summary: dict = {
        "samples": len(points),
        "duration_s": round(duration_s, 1),
        "distance_m": round(distance_m, 1),
        "elevation_gain_m": round(_elevation_gain_m(points), 1),
        "avg_speed_mps": round(avg_speed_mps, 3) if avg_speed_mps is not None else None,
        "power": None,
        "heart_rate": {
            "avg_bpm": round(avg_hr, 1) if avg_hr is not None else None,
            "peak_bpm": peak_hr,
        }
        if hr_series
        else None,
        "cadence": {
            "avg_rpm": round(avg_cad, 1) if avg_cad is not None else None,
            "peak_rpm": peak_cad,
        }
        if cad_series
        else None,
    }

    if power_series:
        np_value = power_math.normalized_power(power_series, sample_rate_hz)
        if_value = power_math.intensity_factor(np_value, ftp)
        tss = power_math.training_stress_score(duration_s, np_value, ftp)
        ppc = power_math.peak_power_curve(power_series, sample_rate_hz=sample_rate_hz)
        tiz = power_math.time_in_zone(power_series, ftp, sample_rate_hz)
        summary["power"] = {
            "ftp_w": ftp,
            "avg_w": round(avg_power, 1) if avg_power is not None else None,
            "peak_w": peak_power,
            "normalized_power_w": round(np_value, 1),
            "intensity_factor": round(if_value, 3),
            "training_stress_score": round(tss, 1),
            "peak_power_curve_w": {str(k): round(v, 1) for k, v in ppc.items()},
            "time_in_zone_s": {k: round(v, 1) for k, v in tiz.items()},
        }

    return summary
