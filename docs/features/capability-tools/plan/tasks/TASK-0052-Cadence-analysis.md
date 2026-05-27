---
type: "[[task]]"
id: TASK-0052
aliases: ["TASK-0052"]
title: "Cadence analysis"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: S
---

# TASK-0052 — Cadence analysis

Given an activity → cadence distribution histogram, time-in-cadence-zones (default: <60 / 60–80 / 80–95 / 95+ rpm), dead-spot detection (sustained segments under 50 rpm indicating coasting), cadence drift across the ride. Useful for technique-focused riders and coaches.

## Acceptance
- [ ] Histogram with configurable bin boundaries.
- [ ] Dead-spot detection: contiguous segments below threshold + minimum duration.
- [ ] Drift: cadence trend across the ride (slope of rolling-average).
- [ ] Stateless.
