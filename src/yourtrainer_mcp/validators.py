"""Structural validators for the registry ``validate`` tool (FEAT-0001).

Each validator answers "is this a well-formed <format> document?" with a list
of errors (and warnings where useful). These are structural checks, not full
schema conformance — enough for an LLM to self-correct a conversion.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from . import fit
from . import workout as wk


def _xml_root_local(text: str) -> tuple[str | None, str | None]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return None, f"XML parse error: {e}"
    return root.tag.rsplit("}", 1)[-1], None


def _validate_zwo(text: str) -> list[str]:
    try:
        w = wk.from_zwo(text)
    except wk.WorkoutError as e:
        return [str(e)]
    return [f"{f['code']}: {f['message']}" for f in wk.lint_workout(w)
            if f["severity"] == "error"]


def _validate_ytw(text: str) -> list[str]:
    try:
        wk.from_ytw(text)
    except wk.WorkoutError as e:
        return [str(e)]
    return []


def _validate_xml_route(text: str, expect_root: str, needs: str | None) -> list[str]:
    root, err = _xml_root_local(text)
    if err:
        return [err]
    if root != expect_root:
        return [f"root element is <{root}>, expected <{expect_root}>"]
    if needs and needs not in text:
        return [f"no <{needs}> elements found"]
    return []


def _validate_erg_mrc(text: str) -> list[str]:
    errors: list[str] = []
    if "[COURSE DATA]" not in text:
        errors.append("missing [COURSE DATA] section")
        return errors
    body = text.split("[COURSE DATA]", 1)[1].split("[END COURSE DATA]", 1)[0]
    rows = 0
    for line in body.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                float(parts[0])
                float(parts[1])
                rows += 1
            except ValueError:
                errors.append(f"non-numeric data row: {line.strip()!r}")
    if rows == 0:
        errors.append("no numeric 'minutes value' rows found")
    return errors


def _validate_fit(text_or_b64: str) -> list[str]:
    import base64
    try:
        data = base64.b64decode(text_or_b64, validate=False)
        fit.decode(data)
    except Exception as e:  # noqa: BLE001
        return [f"FIT decode failed: {e}"]
    return []


def _validate_locale(text: str) -> list[str]:
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            return [f"invalid JSON: {e}"]
        return []
    if stripped.startswith("<"):
        _, err = _xml_root_local(text)
        return [err] if err else []
    # .strings / .po: lightweight non-empty check.
    return [] if stripped else ["empty locale bundle"]


def validate(key: str, document: str) -> dict:
    """Validate ``document`` as format ``key``. Returns {valid, errors}."""
    key = key.lower()
    if key == "zwo":
        errors = _validate_zwo(document)
    elif key == "ytw":
        errors = _validate_ytw(document)
    elif key == "gpx":
        errors = _validate_xml_route(document, "gpx", "trkpt")
    elif key == "tcx":
        errors = _validate_xml_route(document, "TrainingCenterDatabase", None)
    elif key == "kml":
        errors = _validate_xml_route(document, "kml", None)
    elif key in ("erg", "mrc"):
        errors = _validate_erg_mrc(document)
    elif key == "fit":
        errors = _validate_fit(document)
    elif key == "locale":
        errors = _validate_locale(document)
    else:
        return {"valid": False, "errors": [f"no validator for format '{key}'"]}
    return {"valid": not errors, "errors": errors}
