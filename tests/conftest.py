"""Shared fixtures: builders for synthetic TCX/GPX activity files."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


def _iso(base: datetime, offset_s: int) -> str:
    return (base + timedelta(seconds=offset_s)).isoformat().replace("+00:00", "Z")


def build_tcx(powers, *, altitudes=None, base_distance_m=0.0) -> str:
    """Build a minimal but realistic TCX string from a power series.

    One trackpoint per second. Distance accumulates at 10 m/s. Altitude is
    taken from ``altitudes`` (same length) when provided.
    """
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    pts = []
    dist = base_distance_m
    for i, p in enumerate(powers):
        dist += 10.0
        alt = altitudes[i] if altitudes is not None else 100.0
        pts.append(
            f"""        <Trackpoint>
          <Time>{_iso(base, i)}</Time>
          <Position><LatitudeDegrees>52.0</LatitudeDegrees>"""
            f"""<LongitudeDegrees>5.0</LongitudeDegrees></Position>
          <AltitudeMeters>{alt}</AltitudeMeters>
          <DistanceMeters>{dist}</DistanceMeters>
          <HeartRateBpm><Value>{140 + (i % 5)}</Value></HeartRateBpm>
          <Cadence>{90}</Cadence>
          <Extensions><TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">"""
            f"""<Watts>{p}</Watts></TPX></Extensions>
        </Trackpoint>"""
        )
    points = "\n".join(pts)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">\n'
        "  <Activities><Activity Sport=\"Biking\"><Lap><Track>\n"
        f"{points}\n"
        "  </Track></Lap></Activity></Activities>\n"
        "</TrainingCenterDatabase>\n"
    )


def build_gpx(powers=None, *, altitudes=None, n=None) -> str:
    """Build a minimal GPX string. With ``powers`` it embeds power extensions;
    otherwise it is a plain route of ``n`` points (no power)."""
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    count = len(powers) if powers is not None else (n or 0)
    pts = []
    for i in range(count):
        lat = 52.0 + i * 0.001
        lon = 5.0 + i * 0.001
        alt = altitudes[i] if altitudes is not None else 100.0
        ext = ""
        if powers is not None:
            ext = (
                "        <extensions><power>"
                f"{powers[i]}</power></extensions>\n"
            )
        pts.append(
            f'      <trkpt lat="{lat}" lon="{lon}">\n'
            f"        <ele>{alt}</ele>\n"
            f"        <time>{_iso(base, i)}</time>\n"
            f"{ext}"
            "      </trkpt>"
        )
    points = "\n".join(pts)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">\n'
        "  <trk><trkseg>\n"
        f"{points}\n"
        "  </trkseg></trk>\n"
        "</gpx>\n"
    )


@pytest.fixture
def tcx_builder():
    return build_tcx


@pytest.fixture
def gpx_builder():
    return build_gpx
