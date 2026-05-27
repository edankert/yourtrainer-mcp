---
type: "[[task]]"
id: TASK-0021
aliases: ["TASK-0021"]
title: "FIT-activity inspector + NP/IF/TSS calculation"
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

# TASK-0021 — FIT-activity inspector + NP/IF/TSS calculation

Read a recorded ride (FIT-activity), emit a structured JSON summary: duration, distance, elevation gain, peak power, average power, NP (normalised power, Coggan's 30s-rolling-mean-fourth-root), IF (intensity factor = NP/FTP), TSS (training-stress score = (duration × NP × IF) / (FTP × 3600) × 100), time-in-zone breakdown, peak HR, average HR, peak cadence, average cadence, average speed.

## Acceptance
- [ ] Reads FIT, TCX, GPX activity files.
- [ ] Emits structured JSON summary with documented schema.
- [ ] NP / IF / TSS validated against TrainingPeaks reference numbers for ≥5 canonical activities (within ±2% tolerance for NP, exact for IF/TSS given consistent FTP).
- [ ] Time-in-zone breakdown configurable by FTP and zone-boundary preset.
