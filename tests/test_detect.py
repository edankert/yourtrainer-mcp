"""Tests for format detection + lightweight file inspector (TASK-0037)."""

from __future__ import annotations

from yourtrainer_mcp import detect, fit


def test_detect_fit_by_magic_bytes():
    data = fit.encode_activity_fit([{"power": 200}])
    assert detect.detect_format("mislabeled.dat", data[:64]) == "fit"


def test_detect_xml_formats_by_root():
    assert detect.detect_format("x", b"<gpx version='1.1'>") == "gpx"
    assert detect.detect_format("x", b"<?xml ?><workout_file>") == "zwo"
    assert detect.detect_format("x", b"<TrainingCenterDatabase>") == "tcx"


def test_detect_ytw_json():
    assert detect.detect_format("x.bin", b'{"format": "ytw", "steps": []}') == "ytw"


def test_detect_falls_back_to_extension():
    assert detect.detect_format("ride.gpx", None) == "gpx"
    assert detect.detect_format("unknown.xyz", None) is None


def test_inspect_file_reports_format(tmp_path):
    f = tmp_path / "ride.fit"
    f.write_bytes(fit.encode_activity_fit([{"power": 200}]))
    info = detect.inspect_file(f)
    assert info["detected_format"] == "fit"
    assert info["binary"] is True
    assert info["size_bytes"] > 0
