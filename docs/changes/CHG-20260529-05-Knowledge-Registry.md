---
type: "[[change]]"
id: CHG-20260529-05
title: "Knowledge registry corpus + registry/validator tools (Wave 4)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["knowledge-registry", "mcp-server", "packaging"]
issues: []
features: ["[[FEAT-0001]]"]
related: ["[[TASK-0002]]", "[[TASK-0003]]", "[[TASK-0004]]", "[[TASK-0005]]", "[[TASK-0006]]", "[[TASK-0007]]", "[[TST-0005]]"]
---

# Knowledge registry corpus + registry/validator tools (Wave 4)

## Summary
Authored the FEAT-0001 knowledge corpus and the tools that surface it:
- `src/yourtrainer_mcp/specs/*.json` — 9 formats (zwo, erg, mrc, fit, gpx, tcx,
  kml, ytw, locale), each with a spec summary, ≥3 canonical examples, per-app
  constraints, conversion notes, glossary, and version.
- `registry.py` — loads the packaged corpus via importlib.resources and exposes
  spec/examples/constraints/conversion-notes/glossary/version queries.
- `validators.py` — structural `validate(format, document)` for each format.
- Added the `locale` entry to the supported-formats catalogue.

MCP tools wired: `get_format_spec`, `get_canonical_examples`,
`get_format_constraints`, `get_conversion_notes`, `get_format_glossary`,
`get_format_version`, `validate`.

## Impact
- New packaged data files (`specs/*.json`) — confirmed included in the wheel,
  so a plain `pip install .` deploy on the VPS ships the corpus.
- Knowledge layer (FEAT-0001) is now functional alongside the capability layer.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0001 — corpus + tools live)
- requirements: not-applicable
- tasks: updated (TASK-0002..0007 → done)
- issues: not-applicable
- tests: new (TST-0005)
- workflows: not-applicable
- decisions: not-applicable
- risks: noted — corpus accuracy is subject to RISK-0003 (format-spec drift)
- changes: new (this note)
- snapshot: updated (statuses, counters, metrics, focus → Wave 5)

## Verification
- `pytest -q` → 92 passed. ruff + mypy clean. Wheel ships 9 spec files.

## Follow-ups
- [ ] TASK-0041 (Hypothesis property tests + golden files) and TASK-0045
  (TrainingPeaks/Intervals.icu reference corpus) remain open under FEAT-0001.
- [ ] Public docs-site mirror of the corpus (later FEAT-0001 task).
- [ ] Corpus accuracy reviews tracked under RISK-0003 (format-spec drift).
