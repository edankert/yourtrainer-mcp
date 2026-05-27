---
type: "[[task]]"
id: TASK-0020
aliases: ["TASK-0020"]
title: "FIT-workout read/write tool (binary, Garmin SDK)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: L
---

# TASK-0020 — FIT-workout read/write tool (binary, Garmin SDK)

Implement read + write for Garmin's FIT-workout binary format using the official FIT SDK Python (or TS) bindings. Tool reads a FIT-workout file → emits a structured JSON representation; writes the inverse direction.

## Acceptance
- [ ] Reads canonical FIT-workout files from Garmin Connect / Wahoo X / TrainingPeaks exports.
- [ ] Emits valid FIT-workout files importable on a Garmin Edge (manual test on a paired device).
- [ ] Round-trips: read → write → read preserves all fields within FIT's quantisation.
- [ ] Test suite includes ≥10 canonical FIT-workout samples.
