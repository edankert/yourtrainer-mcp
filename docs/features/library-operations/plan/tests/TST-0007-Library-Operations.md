---
type: "[[test]]"
id: TST-0007
title: "Library operations suite (index/dedup/stats/best-efforts)"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0038]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_library.py"
requirements: []
features: ["[[FEAT-0006]]"]
issues: []
tasks: ["[[TASK-0038]]", "[[TASK-0039]]", "[[TASK-0040]]", "[[TASK-0049]]"]
artifacts: ["tests/test_library.py", "src/yourtrainer_mcp/library.py"]
evidence: ["118 passed (full suite)"]
last_run: "2026-05-29"
related: []
---

# Library operations suite

## Purpose
Verify FEAT-0006: metadata indexing across mixed workout/activity files,
near-duplicate detection, aggregate statistics, and the all-time best-efforts
curve.

## Expected results
- Index mixes workouts and activities; reports kind/format/duration/TSS.
- Two workouts with the same power profile (even in different formats) are
  grouped as duplicates; a distinct workout is not.
- Stats aggregate file counts, total duration, and total TSS.
- Best-efforts-across-history attributes each duration's peak to its source file.

## Evidence
- `118 passed`; ruff + mypy clean.
