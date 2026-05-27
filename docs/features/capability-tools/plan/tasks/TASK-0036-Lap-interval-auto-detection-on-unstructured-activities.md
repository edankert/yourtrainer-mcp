---
type: "[[task]]"
id: TASK-0036
aliases: ["TASK-0036"]
title: "Lap / interval auto-detection on unstructured activities"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

# TASK-0036 — Lap / interval auto-detection on unstructured activities

Tool that detects sustained efforts (intervals) in an unstructured activity file. Useful for *post-hoc* analysis when no plan exists or when the rider deviates from the plan. Returns list of detected efforts with start, end, duration, average + peak power, average cadence, suspected intent (warmup / endurance / sweet-spot / threshold / V02max / sprint based on power-zone classification + duration heuristics).

## Acceptance
- [ ] Detects efforts using a documented sliding-window peak-finder + minimum-duration threshold.
- [ ] Each detected effort: `{start_offset_s, end_offset_s, duration_s, avg_power, peak_power, avg_cadence, avg_hr, classification, confidence}`.
- [ ] Configurable: detection sensitivity, minimum effort duration, FTP for zone classification.
- [ ] Validated against ≥5 canonical activities with known interval structure.
- [ ] Stateless.
