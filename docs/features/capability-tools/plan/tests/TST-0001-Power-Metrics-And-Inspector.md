---
type: "[[test]]"
id: TST-0001
title: "NP/IF/TSS + activity-inspector unit suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0021]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q"
requirements: []
features: ["[[FEAT-0004]]", "[[FEAT-0001]]", "[[FEAT-0003]]"]
issues: []
tasks: ["[[TASK-0021]]"]
artifacts: ["tests/test_power.py", "tests/test_activity.py", "tests/test_attribution.py", "tests/test_server.py"]
evidence: ["26 passed in 0.58s (Python 3.13.13, local)"]
last_run: "2026-05-29"
related: ["[[ADR-0003]]", "[[ADR-0001]]"]
---

# NP/IF/TSS + activity-inspector unit suite

## Purpose
Verify the v1 capability engine (TASK-0021): the Coggan power/training-load math,
TCX/GPX activity parsing, the activity-inspector summary schema, and the
attribution invariant (FEAT-0003).

## Procedure
- `pip install -e ".[dev]"`
- `pytest -q`
- (lint/type gates) `ruff check src tests` and `mypy src`

## Expected results
- All tests pass.
- Canonical anchors hold:
  - Constant power ⇒ NP == power.
  - 1 hour at FTP ⇒ IF == 1.0, TSS == 100.
  - Variable power ⇒ NP > average power.
- Inspector emits the documented JSON summary; routes without power return a
  `null` power block; non-positive FTP and unsupported extensions raise.
- Attribution is always present; the `.ytw` hint appears only when referenced;
  no comparative content (POSITIONING Principle 1).

## Evidence (fill after running)
- `26 passed in 0.58s` — pytest, Python 3.13.13.
- `ruff check`: All checks passed. `mypy src`: Success: no issues found in 6 source files.
- End-to-end: `inspect_activity` on a 20-min 300/150 W TCX ⇒ NP 247.2, IF 0.989,
  TSS 32.6, time-in-zone Z2 600 s / Z5 600 s (as expected).

## Remaining for TASK-0021 → done
- FIT-binary fixtures + a real-file read test (the `fitparse` path is implemented
  but not yet covered by a fixture).
- TrainingPeaks/Intervals.icu reference corpus validation (TASK-0045): ≥5
  canonical activities within ±2% NP.
- Configurable time-in-zone presets beyond the Coggan default.
