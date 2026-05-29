"""Tests for the knowledge registry + validators (FEAT-0001)."""

from __future__ import annotations

import base64

import pytest

from yourtrainer_mcp import fit_workout, registry, validators
from yourtrainer_mcp import workout as wk

EXPECTED_KEYS = {"zwo", "erg", "mrc", "fit", "gpx", "tcx", "kml", "ytw", "locale"}


def test_registry_covers_all_formats():
    assert EXPECTED_KEYS.issubset(set(registry.format_keys()))


@pytest.mark.parametrize("key", sorted(EXPECTED_KEYS))
def test_each_format_has_spec_examples_constraints_glossary(key):
    spec = registry.get_spec(key)
    assert spec["spec"] and spec["name"]
    assert len(registry.get_examples(key)) >= 3, f"{key} needs >=3 examples"
    assert registry.get_constraints(key)
    assert registry.get_conversion_notes(key) or key in ("locale",)
    assert registry.get_glossary(key)
    assert registry.get_version(key)


def test_unknown_format_raises():
    with pytest.raises(registry.UnknownFormat):
        registry.get_spec("nope")


def test_no_comparative_content_in_corpus():
    # POSITIONING Principle 1: corpus must not disparage other apps.
    banned = ["better than", "worse than", "superior to", "inferior to"]
    for key in registry.format_keys():
        blob = str(registry.get_format(key)).lower()
        for phrase in banned:
            assert phrase not in blob, f"{key} contains comparative phrase {phrase!r}"


# ---- validators ----

def test_validate_zwo_roundtrip_is_valid():
    w = wk.build_workout({"name": "v", "steps": [
        {"kind": "warmup", "duration_s": 300, "power_low": 0.4, "power_high": 0.7},
        {"kind": "steady", "duration_s": 600, "power": 0.85}]})
    assert validators.validate("zwo", wk.to_zwo(w))["valid"] is True


def test_validate_zwo_garbage_is_invalid():
    assert validators.validate("zwo", "<not-a-workout/>")["valid"] is False


def test_validate_ytw():
    valid_doc = '{"format":"ytw","steps":[{"kind":"freeride","duration_s":60}]}'
    assert validators.validate("ytw", valid_doc)["valid"]
    assert not validators.validate("ytw", '{"format":"nope"}')["valid"]


def test_validate_gpx_requires_trkpt():
    good = "<gpx><trk><trkseg><trkpt lat='1' lon='2'/></trkseg></trk></gpx>"
    assert validators.validate("gpx", good)["valid"]
    bad = validators.validate("gpx", "<gpx></gpx>")
    assert not bad["valid"] and "trkpt" in bad["errors"][0]


def test_validate_erg_needs_numeric_rows():
    good = ("[COURSE HEADER]\nMINUTES WATTS\n[END COURSE HEADER]\n"
            "[COURSE DATA]\n0 200\n20 200\n[END COURSE DATA]")
    assert validators.validate("erg", good)["valid"]
    assert not validators.validate("erg", "[COURSE HEADER]\n[END COURSE HEADER]")["valid"]


def test_validate_fit_base64():
    w = wk.build_workout(
        {"name": "f", "steps": [{"kind": "steady", "duration_s": 60, "power": 0.8}]}
    )
    b64 = base64.b64encode(fit_workout.encode_workout_fit(w)).decode("ascii")
    assert validators.validate("fit", b64)["valid"] is True
    assert not validators.validate("fit", base64.b64encode(b"junk").decode())["valid"]
