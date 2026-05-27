---
type: "[[task]]"
id: TASK-0049
aliases: ["TASK-0049"]
title: "Best-efforts-across-history"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
---

# TASK-0049 — Best-efforts-across-history

Given a folder of activities + one or more target durations, return the all-time best mean-max power at each duration, plus the activity date and (when GPX-backed) the location where it occurred. Composes peak-power-curve (TASK-0022) across multiple files. Answers *"when did I last hit my best 20-min power?"* — a common question paid analytics services answer.

## Acceptance
- [ ] Accepts folder of activities + list of target durations (default: 5s / 1min / 5min / 20min / 60min).
- [ ] Per-duration result: `{duration_s, best_power_w, activity_id, activity_date, location_km_into_ride, location_coords (optional)}`.
- [ ] Top-N per duration optional (e.g. top-5 best 20-min efforts of the season).
- [ ] Handles ≥500 activities without memory blow-up.
- [ ] Stateless.
