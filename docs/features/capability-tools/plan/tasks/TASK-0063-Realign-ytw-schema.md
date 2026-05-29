---
type: "[[task]]"
id: TASK-0063
aliases: ["TASK-0063"]
title: "Realign workout model + .ytw writer/reader to the canonical Your Trainer schema (ISS-0001)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: ["[[ISS-0001]]"]
effort: L
---

# TASK-0063 — Realign workout model + .ytw to the canonical schema

Rebuilt `workout.py` around the canonical Your Trainer schema:
- **Model**: Block / Repeat / Cue / Workout; power as integer % FTP; intervals as
  a flat list of blocks + (nestable) repeat groups; warmup/cooldown via intervalType.
- **build_workout** input mirrors `workout-intent.json` (warmup/intervals/cooldown).
- **to_ytw** emits canonical `.ytw` (programId, intervals with intervalType /
  targetPowerPercent / repeat groups, strings); **from_ytw** parses it.
- ZWO + FIT + difficulty + scale + lint + app-acceptance + adherence adapted;
  fit_workout rewritten (integer %FTP -> exact round-trips).

## Verification (against the canonical schema)
- Cross-checked field-for-field against `your-trainer/docs/ytw-schema.json`,
  `generate_workout_library.py`, and the published
  `your-applications.com/your-trainer/workout-schema.html`.
- Caught two stale points in `ytw-schema.json` vs the canonical page and matched
  the page: **workoutType (POWER/HR_ZONE/ROUTE) and variant (STANDARD/RAMP_TEST)
  are separate fields**, and **repeat groups can nest** — both now supported.
- Difficulty matches the website manifest values (e.g. sweet-spot-3x10 -> TSS 58.4,
  IF 0.764). 192 tests; ytw/zwo/fit round-trips exact incl. nested repeats.

> **Done 2026-05-29 (CHG-20260529-15).** Fixes [[ISS-0001]].
