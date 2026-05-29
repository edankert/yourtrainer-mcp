---
type: "[[test]]"
id: TST-0002
title: "Workout authoring unit suite (build/decompose/scale/lint/difficulty/acceptance)"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0023]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_workout.py"
requirements: []
features: ["[[FEAT-0004]]"]
issues: []
tasks: ["[[TASK-0023]]", "[[TASK-0033]]", "[[TASK-0035]]", "[[TASK-0025]]", "[[TASK-0050]]", "[[TASK-0024]]"]
artifacts: ["tests/test_workout.py", "src/yourtrainer_mcp/workout.py"]
evidence: ["40 passed in 0.65s (full suite, Python 3.13.13)"]
last_run: "2026-05-29"
related: ["[[ADR-0003]]"]
---

# Workout authoring unit suite

## Purpose
Verify the workout-authoring cluster: build-from-intent, ZWO/.ytw render,
decompose (inverse), scale, lint, difficulty score, and app-acceptance.

## Procedure
- `pytest -q` (or `pytest -q tests/test_workout.py`)

## Expected results
- Build validates required fields per step kind; rejects unknown kinds / empty steps.
- ZWO and .ytw round-trip preserves step kinds, durations, power fractions, cadence.
- Scale: `duration_factor` changes durations only; `intensity_factor` changes power
  fractions only; non-positive factors rejected.
- Difficulty is FTP-independent (same TSS for FTP 250 and 300).
- Lint flags zero-duration, missing warmup, missing name, implausible power.
- App-acceptance flags FreeRide on Garmin and over-long names.

## Evidence
- `40 passed in 0.65s`; ruff + mypy clean.
- End-to-end: a 4×4 VO2max build → IF 0.892, TSS 62.4, 960 s in Z5; valid ZWO;
  decompose + 50%-duration scale verified.
