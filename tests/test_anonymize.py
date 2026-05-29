"""Tests for activity anonymisation (TASK-0030)."""

from __future__ import annotations

from yourtrainer_mcp.activity import parse_gpx
from yourtrainer_mcp.anonymize import anonymize_gpx

GPX_WITH_HR = """<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><trkseg>
    <trkpt lat="52.00000" lon="5.00000"><ele>10</ele>
      <extensions><hr>140</hr><power>200</power></extensions></trkpt>
    <trkpt lat="52.01000" lon="5.00000"><ele>12</ele>
      <extensions><hr>150</hr><power>210</power></extensions></trkpt>
    <trkpt lat="52.02000" lon="5.00000"><ele>14</ele>
      <extensions><hr>155</hr><power>220</power></extensions></trkpt>
    <trkpt lat="52.03000" lon="5.00000"><ele>16</ele>
      <extensions><hr>160</hr><power>205</power></extensions></trkpt>
  </trkseg></trk>
</gpx>"""


def test_privacy_zone_removes_start_and_end_points():
    out = anonymize_gpx(GPX_WITH_HR, privacy_radius_m=200.0)
    assert out["removed_points"] >= 2  # at least the start and end points
    assert out["kept_points"] + out["removed_points"] == 4
    # Output is valid GPX and parses.
    pts = parse_gpx(out["gpx"])
    assert len(pts) == out["kept_points"]


def test_drop_hr_removes_heart_rate():
    out = anonymize_gpx(GPX_WITH_HR, privacy_radius_m=50.0, drop_hr=True)
    assert "<hr>" not in out["gpx"]
    assert out["hr_dropped"] is True
    # Power is retained.
    assert "<power>" in out["gpx"]


def test_keep_hr_by_default():
    out = anonymize_gpx(GPX_WITH_HR, privacy_radius_m=50.0, drop_hr=False)
    assert "<hr>" in out["gpx"]


def test_empty_gpx():
    out = anonymize_gpx("<gpx xmlns='http://www.topografix.com/GPX/1/1'></gpx>")
    assert out["kept_points"] == 0
