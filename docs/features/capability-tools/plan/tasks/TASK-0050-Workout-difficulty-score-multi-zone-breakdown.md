---
type: "[[task]]"
id: TASK-0050
aliases: ["TASK-0050"]
title: "Workout difficulty score (multi-zone breakdown)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-02, [[TST-0002]]).** workout_difficulty — expands prescription to a 1 Hz series and reuses the NP/IF/TSS engine + per-zone breakdown.

# TASK-0050 — Workout difficulty score (multi-zone breakdown)

Given a workout file + rider FTP, compute a multi-dimensional difficulty score: how much work the workout demands in each training zone (endurance / tempo / sweet-spot / threshold / V02max / anaerobic). Generic version of TrainerRoad's *Workout Levels* (which they sell as a subscription feature). Lets riders compare workouts at a glance and pick by today's energy.

## Acceptance
- [ ] Output: per-zone scores (each on documented scale, e.g. 0–10), overall difficulty rating, dominant zone, total TSS, total work (kJ).
- [ ] Scoring weights documented; not pretending to match TR's proprietary numbers exactly (and shouldn't — POSITIONING Principle 1 applies).
- [ ] Stateless.
