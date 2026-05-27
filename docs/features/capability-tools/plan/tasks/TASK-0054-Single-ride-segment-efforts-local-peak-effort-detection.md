---
type: "[[task]]"
id: TASK-0054
aliases: ["TASK-0054"]
title: "Single-ride segment efforts (local peak-effort detection)"
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

# TASK-0054 — Single-ride segment efforts (local peak-effort detection)

Within a single ride file, find the strongest 20s / 1min / 5min / 20min efforts with their start/end timestamps + (for GPX-backed activities) location coordinates. Local version of Strava-style segments without the multi-rider leaderboard. Useful for *"how did my V02 efforts go in today's ride?"* without a structured plan.

## Acceptance
- [ ] Per-duration peak effort returned: `{duration_s, peak_avg_power, start_offset_s, end_offset_s, start_coords (optional), end_coords (optional)}`.
- [ ] Top-N per duration optional (default: top 1 per duration).
- [ ] Stateless.
