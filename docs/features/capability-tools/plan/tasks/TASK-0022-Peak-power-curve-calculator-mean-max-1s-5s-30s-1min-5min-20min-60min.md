---
type: "[[task]]"
id: TASK-0022
aliases: ["TASK-0022"]
title: "Peak power curve calculator (mean-max 1s, 5s, 30s, 1min, 5min, 20min, 60min)"
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

# TASK-0022 — Peak power curve calculator (mean-max 1s, 5s, 30s, 1min, 5min, 20min, 60min)

Read an activity file, compute the mean-max power curve at standard durations. Output: `{duration_seconds: peak_watts}` plus the timestamp ranges where each peak occurred. Useful for: rider power-profile analysis, season-over-season comparison, fitness-tracking dashboards.

## Acceptance
- [ ] Computes mean-max correctly per the canonical algorithm (sliding window, peak = max of windowed averages).
- [ ] Validates against canonical activities with known peaks (within ±1W tolerance).
- [ ] Returns timestamp ranges for each peak, not just the value.
- [ ] Performance: handles a 5-hour activity in <2 seconds.
