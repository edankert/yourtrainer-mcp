"""Knowledge-registry format catalogue (FEAT-0001 — stub).

This is the v1 seed of the supported-formats catalogue surfaced by the
``list_supported_formats`` MCP tool. The full per-format corpus (spec,
examples, constraints, conversion notes, glossary) lands under ``specs/``
in later FEAT-0001 tasks (TASK-0002..0007); this module enumerates what the
registry covers so the tool is wired and testable today.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormatInfo:
    key: str
    name: str
    kind: str  # "workout" | "activity" | "route" | "locale"
    binary: bool
    extensions: tuple[str, ...]


SUPPORTED_FORMATS: tuple[FormatInfo, ...] = (
    FormatInfo("zwo", "Zwift Workout", "workout", False, (".zwo",)),
    FormatInfo("erg", "ERG (PerfPRO/TrainerRoad)", "workout", False, (".erg",)),
    FormatInfo("mrc", "MRC", "workout", False, (".mrc",)),
    FormatInfo("fit", "Flexible and Interoperable Data Transfer", "activity", True, (".fit",)),
    FormatInfo("gpx", "GPS Exchange Format", "activity", False, (".gpx",)),
    FormatInfo("tcx", "Training Center XML", "activity", False, (".tcx",)),
    FormatInfo("kml", "Keyhole Markup Language", "route", False, (".kml",)),
    FormatInfo("ytw", "Your Trainer Workout", "workout", False, (".ytw",)),
)


def list_supported_formats() -> list[dict]:
    """Catalogue of formats the registry covers."""
    return [
        {
            "key": f.key,
            "name": f.name,
            "kind": f.kind,
            "binary": f.binary,
            "extensions": list(f.extensions),
        }
        for f in SUPPORTED_FORMATS
    ]
