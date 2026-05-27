---
type: "[[task]]"
id: TASK-0029
aliases: ["TASK-0029"]
title: "Pacing strategy generator (GPX route + FTP + target effort → pacing plan)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: L
---

# TASK-0029 — Pacing strategy generator (GPX route + FTP + target effort → pacing plan)

Given a GPX route + rider FTP + target effort level (e.g. 'tempo', 'threshold', 'all-out') + optional target time, generate a per-segment pacing plan with power, HR, and cadence targets that account for elevation gradient (harder on climbs within reason, easier on descents) and accumulated fatigue. Output: structured pacing plan (JSON) + exportable as a `.ytw` / FIT-workout for execution. Stateless.

## Acceptance
- [ ] Reads valid GPX routes; respects elevation profile + segment distance.
- [ ] Pacing model accounts for: gradient-adjusted power, NP target, IF cap based on effort level, fatigue drift across distance.
- [ ] Output validates against canonical pacing references (Best Bike Split-style outputs within ±5% on canonical routes).
- [ ] Pacing plan exportable to `.ytw` + FIT-workout via FEAT-0004 workout builder.
- [ ] Stateless: route + FTP in, plan out, nothing retained.
