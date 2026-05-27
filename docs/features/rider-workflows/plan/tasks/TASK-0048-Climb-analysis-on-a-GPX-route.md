---
type: "[[task]]"
id: TASK-0048
aliases: ["TASK-0048"]
title: "Climb analysis on a GPX route"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: M
---

# TASK-0048 — Climb analysis on a GPX route

Given a GPX route, detect climbs using documented heuristics (sustained gradient ≥3% over ≥500m, with configurable thresholds). For each climb: start/end offsets, length, average + max gradient, elevation gain, FIETS index (length × grade²), category (HC / Cat 1 / 2 / 3 / 4). Pairs naturally with the pacing strategy generator (TASK-0029) — feed climb data into pacing plan to allow per-climb effort calibration.

## Acceptance
- [ ] Reads valid GPX routes; outputs structured climb list.
- [ ] Per-climb fields: `{start_offset_km, end_offset_km, length_km, avg_grade_pct, max_grade_pct, elevation_gain_m, fiets_index, category}`.
- [ ] Detection thresholds configurable; defaults match cycling convention.
- [ ] Cross-validated against RideWithGPS / Komoot climb detection for canonical routes (allow ±10% tolerance on climb boundaries).
- [ ] Stateless.
