---
type: "[[test]]"
id: TST-0005
title: "Knowledge registry corpus + validators suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0002]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_registry.py"
requirements: []
features: ["[[FEAT-0001]]"]
issues: []
tasks: ["[[TASK-0002]]", "[[TASK-0003]]", "[[TASK-0004]]", "[[TASK-0005]]", "[[TASK-0006]]", "[[TASK-0007]]"]
artifacts: ["tests/test_registry.py", "src/yourtrainer_mcp/registry.py", "src/yourtrainer_mcp/validators.py", "src/yourtrainer_mcp/specs/"]
evidence: ["92 passed (full suite); 9 spec files ship in the built wheel"]
last_run: "2026-05-29"
related: []
---

# Knowledge registry corpus + validators suite

## Purpose
Verify the FEAT-0001 corpus and the registry/validator surface: every format
has a spec, ≥3 examples, constraints, conversion notes, and a glossary; the
corpus is POSITIONING-compliant; and structural validators accept good docs
and reject malformed ones.

## Expected results
- `registry.format_keys()` covers zwo/erg/mrc/fit/gpx/tcx/kml/ytw/locale.
- Each format: spec text present, ≥3 examples, non-empty constraints + glossary,
  a version string.
- No comparative phrasing anywhere in the corpus (Principle 1).
- `validate()` accepts a built ZWO/.ytw/FIT and a well-formed GPX/ERG; rejects
  malformed ones (bad XML root, missing trkpt, no numeric rows, junk FIT).
- The 9 spec JSON files are packaged in the wheel (verified via `python -m build`).

## Evidence
- `92 passed in 0.98s`; ruff + mypy clean.
- Wheel inspection: `yourtrainer_mcp/specs/*.json` × 9 present.
