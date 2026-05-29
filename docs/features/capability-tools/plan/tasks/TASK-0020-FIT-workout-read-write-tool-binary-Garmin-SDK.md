---
type: "[[task]]"
id: TASK-0020
aliases: ["TASK-0020"]
title: "FIT-workout read/write tool (binary, Garmin SDK)"
status: doing
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: L
---

# TASK-0020 — FIT-workout read/write tool (binary, Garmin SDK)

Implement read + write for Garmin's FIT-workout binary format using the official FIT SDK Python (or TS) bindings. Tool reads a FIT-workout file → emits a structured JSON representation; writes the inverse direction.

## Acceptance
- [~] Reads canonical FIT-workout files. Built-in codec reads standard (non-compressed,
  non-developer-field) FIT; the `fitparse` extra handles richer real-world files.
  Validation against actual Garmin/Wahoo/TP exports pending real sample files.
- [ ] Emits valid FIT-workout files importable on a Garmin Edge — needs an on-device test.
- [x] Round-trips: write → read preserves the per-second power profile within FIT's
  %FTP integer quantisation (≤0.5% FTP). Bytes independently validated by `fitparse`.
- [~] Test suite: hermetic round-trip + cross-library checks in place; ≥10 canonical
  real-world samples still to be collected.

> **In progress 2026-05-29 (CHG-20260529-03, [[TST-0003]]).** Implemented a
> dependency-free FIT codec (`fit.py`, `fit_workout.py`) per ADR-0001 instead of
> bundling the Garmin SDK. Encode/decode + base64 MCP tools (`build_workout_from_intent`
> output_format=fit, `read_fit_workout`) work and are cross-validated with `fitparse`.
> Remaining for `done`: real Garmin/Wahoo/TP sample corpus + paired-device import test.

> **Progress 2026-05-29 (CHG-20260529-10, [[TST-0011]]).** Now reads real Garmin FIT workout files (WorkoutIndividualSteps/RepeatSteps/CustomTargetValues from python-fitparse, MIT) via our own codec, plus a real Activity.fit. Still open for done: >=10 sample corpus + on-device Edge import test.
