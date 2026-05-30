"""Lightweight file inspector + format detection (TASK-0037).

Sniffs a cycling file's format from its content (magic bytes / root element /
JSON marker), falling back to the extension. Content-based so it is robust to
mis-named files on the import path.
"""

from __future__ import annotations

from pathlib import Path

from .formats import SUPPORTED_FORMATS

_EXT_TO_KEY = {ext: f.key for f in SUPPORTED_FORMATS for ext in f.extensions}


def detect_format(filename: str, head: bytes | None = None) -> str | None:
    """Return a format key (e.g. ``"fit"``) or ``None`` if unrecognised.

    ``head`` is the first chunk of file content (≥64 bytes recommended). When
    omitted, detection is by extension only.
    """
    if head is not None:
        # FIT: ".FIT" signature at byte offset 8.
        if len(head) >= 12 and head[8:12] == b".FIT":
            return "fit"
        try:
            text = head.decode("utf-8", "ignore").lstrip()
        except Exception:  # pragma: no cover - decode is lenient
            text = ""
        lowered = text.lower()
        if "<workout_file" in lowered:
            return "zwo"
        if "<gpx" in lowered:
            return "gpx"
        if "<trainingcenterdatabase" in lowered:
            return "tcx"
        if "<kml" in lowered:
            return "kml"
        if text.startswith("{") and ('"programid"' in lowered or '"ytw"' in lowered):
            return "ytw"
    return _EXT_TO_KEY.get(Path(filename).suffix.lower())


def inspect_file(path: str | Path) -> dict:
    """Lightweight 'what is this?' summary without fully parsing the file."""
    path = Path(path)
    head = b""
    if path.exists():
        with path.open("rb") as fh:
            head = fh.read(512)
    key = detect_format(path.name, head if head else None)
    info = next((f for f in SUPPORTED_FORMATS if f.key == key), None)
    return {
        "filename": path.name,
        "detected_format": key,
        "kind": info.kind if info else None,
        "binary": info.binary if info else None,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def inspect_bytes(data: bytes) -> dict:
    """Lightweight 'what is this?' summary for inline (uploaded) content."""
    key = detect_format("", data[:512])
    info = next((f for f in SUPPORTED_FORMATS if f.key == key), None)
    return {
        "filename": None,
        "detected_format": key,
        "kind": info.kind if info else None,
        "binary": info.binary if info else None,
        "size_bytes": len(data),
    }
